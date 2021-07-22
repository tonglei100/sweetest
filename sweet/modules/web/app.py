from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.select import Select
from time import sleep
import re

from sweet import log, vars
from sweet.utility import compare, replace, json2dict

from sweet.modules.web.window import Windows
from sweet.modules.web.locator import locating
from sweet.modules.web.config import *


class App:

    keywords = keywords

    def __init__(self, setting):
        browserName = setting.get('browserName', '')
        headless = setting.pop('headless', False)
        # snapshot = setting.pop('snapshot', False)
        executable_path = setting.pop('executable_path', False)
        # server_url = setting.pop('server_url', '')

        if browserName.lower() == 'ie':
            if executable_path:
                self.driver = webdriver.Ie(executable_path=executable_path)
            else:
                self.driver = webdriver.Ie()
        elif browserName.lower() == 'firefox':
            profile = webdriver.FirefoxProfile()
            profile.accept_untrusted_certs = True

            options = webdriver.FirefoxOptions()
            # 如果配置了 headless 模式
            if headless:
                options.set_headless()
                # options.add_argument('-headless')
                options.add_argument('--disable-gpu')
                options.add_argument("--no-sandbox")
                options.add_argument('window-size=1920x1080')

            if executable_path:
                self.driver = webdriver.Firefox(
                    firefox_profile=profile, firefox_options=options, executable_path=executable_path)
            else:
                self.driver = webdriver.Firefox(
                    firefox_profile=profile, firefox_options=options)
            self.driver.maximize_window()
        elif browserName.lower() == 'chrome':
            options = webdriver.ChromeOptions()

            # 如果配置了 headless 模式
            if headless:
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')
                options.add_argument("--no-sandbox")
                options.add_argument('window-size=1920x1080')

            options.add_argument("--start-maximized")
            options.add_argument('--ignore-certificate-errors')
            # 指定浏览器分辨率，当"--start-maximized"无效时使用
            # options.add_argument('window-size=1920x1080')
            prefs = {}
            prefs["credentials_enable_service"] = False
            prefs["profile.password_manager_enabled"] = False
            options.add_experimental_option("prefs", prefs)
            options.add_argument('disable-infobars')
            options.add_experimental_option(
                "excludeSwitches", ['load-extension', 'enable-automation', 'enable-logging'])
            if executable_path:
                self.driver = webdriver.Chrome(
                    options=options, executable_path=executable_path)
            else:
                self.driver = webdriver.Chrome(options=options)
        else:
            raise Exception(
                'Error: this browser is not supported or mistake name：%s' % browserName)
        # 等待元素超时时间
        self.driver.implicitly_wait(element_wait_timeout)  # seconds
        # 页面刷新超时时间
        self.driver.set_page_load_timeout(page_flash_timeout)  # seconds
        self.w = Windows()
        self.w.driver = self.driver

    def _close(self):
        self.w.close()

    def _call(self, step):
        # 处理截图数据
        # snap = Snapshot()
        # snap.pre(step)

        name = step['data'].pop('#tab', '')
        if name:
            self.w.tab(name)
        else:
            self.w.switch()

        frame = replace(step.get('frame', ''))
        self.w.switch_frame(frame)

        # 根据关键字调用关键字实现
        element = getattr(self, step['keyword'].lower())(step)
        # snap.web_shot(step, element)


    def title(self, data, output):
        log.debug(f'DATA:{repr(data["text"])}')
        log.debug(f'REAL:{repr(self.driver.title)}')
        # try:
        if data['text'].startswith('*'):
            assert data['text'][1:] in self.driver.title
        else:
            assert data['text'] == self.driver.title

        for key in output:
            vars.put({key: self.driver.title})


    def current_url(self, data, output):
        log.debug(f'DATA:{repr(data["text"])}')
        log.debug(f'REAL:{repr(self.driver.current_url)}')
        try:
            if data['text'].startswith('*'):
                assert data['text'][1:] in self.driver.current_url
            else:
                assert data['text'] == self.driver.current_url
        except:
            raise Exception(
                f'check failure, DATA:{data["text"]}, REAL:{self.driver.current_url}')
        # 只能获取到元素 url
        for key in output:
            vars.put({key: self.driver.current_url})

    def locat(self, element, action=''):
        if not isinstance(element, dict):
            raise Exception(f'no this element:{element}')
        return locating(self.driver, element, action=action)

    def open(self, step):
        if isinstance(step['element'], dict):
            url = step['element']['value']
        else:
            url = step['element']
            
        if step['data'].get('#clear', ''):
            self.driver.delete_all_cookies()

        self.driver.get(url)

        cookie = step['data'].get('cookie', '')
        if cookie:
            self.driver.add_cookie(json2dict(cookie))
            co = self.driver.get_cookie(json2dict(cookie).get('name', ''))
            log.debug(f'cookie is add: {co}')
        sleep(0.5)

    def check(self, step):
        data = step['data']
        if not data:
            data = step['expected']
        element = step['element']
        by = element['by']            
        output = step['output']

        location = ''
        if by in ('title', 'current_url'):
            getattr(self, by)(data, output)
        else:
            location = self.locat(element)
            for key in data:
                # 预期结果
                expected = data[key]
                # 切片操作处理
                s = re.findall(r'\[.*?\]', key)
                if s:
                    s = s[0]
                    key = key.replace(s, '')

                if key == 'text':
                    real = location.text
                else:
                    real = location.get_attribute(key)
                if s:
                    real = eval('real' + s)

                log.debug(f'DATA:{repr(expected)}')
                log.debug('REAL:{repr(real)}')
                try:
                    compare(expected, real)
                except:
                    raise Exception(
                        f'check failure, DATA:{repr(expected)}, REAL:{repr(real)}')

            # 获取元素其他属性
            for key in output:
                if output[key] == 'text':
                    v = location.text
                    vars.put({key: v})
                elif output[key] in ('text…', 'text...'):
                    if location.text.endswith('...'):
                        v = location.text[:-3]
                        vars.put({key: v})
                    else:
                        v = location.text
                        vars.put({key: v})
                else:
                    v = location.get_attribute(output[key])
                    vars.put({key: v})
            
        return location
        

    def notcheck(self, step):
        try:
            self.check(step)
            raise Exception('check is success')
        except:
            pass

    def input(self, step):
        data = step['data']
        location = self.locat(step['element'])

        if step['data'].get('清除文本', '') == '否' or step['data'].get('clear', '').lower() == 'no':
            pass
        else:
            location.clear()

        for key in data:
            if key.startswith('text'):
                if isinstance(data[key], tuple):
                    location.send_keys(*data[key])
                elif location:
                    location.send_keys(data[key])
                sleep(0.5)
            if key == 'word':  # 逐字输入
                for d in data[key]:
                    location.send_keys(d)
                    sleep(0.3)
        return location

    def click(self, step):
        data = step['data']

        location = ''
        for element in step.get('elements'):
            # location = locating(self.driver, element, 'CLICK')
            location = self.locat(element, 'CLICK')
            try:
                location.click()
            except ElementClickInterceptedException:  # 如果元素为不可点击状态，则等待1秒，再重试一次
                sleep(1)
                if data.get('mode'):
                    self.driver.execute_script(
                        "arguments[0].click();", location)
                else:
                    location.click()
            sleep(0.5)

        # 获取元素其他属性
        output = step['output']
        for key in output:
            if output[key] == 'text':
                vars.put({key: location.text})
            elif output[key] == 'tag_name':
                vars.put({key: location.tag_name})                
            elif output[key] in ('text…', 'text...'):
                if location.text.endswith('...'):
                    vars.put({key: location.text[:-3]})
                else:
                    vars.put({key: location.text})
            else:
                vars.put({key: location.get_attribute(output[key])})

        return location

    def select(self, step):
        data = step['data']

        location = self.locat(step['element'])
        for key in data:
            if key.startswith('index'):
                Select(location).select_by_index(data[key])
            elif key.startswith('value'):
                Select(location).select_by_value(data[key])
            elif key.startswith('text') or key.startswith('visible_text'):
                Select(location).select_by_visible_text(data[key])

    def deselect(self, step):
        data = step['data']
        location = self.locat(step['element'])
        for key in data:
            if key.startswith('all'):
                Select(location).deselect_all()
            elif key.startswith('index'):
                Select(location).deselect_by_index(data[key])
            elif key.startswith('value'):
                Select(location).deselect_by_value(data[key])
            elif key.startswith('text') or key.startswith('visible_text'):
                Select(location).deselect_by_visible_text(data[key])

    def hover(self, step):
        actions = ActionChains(self.driver)
        location = self.locat(step['element'])
        actions.move_to_element(location)
        actions.perform()
        sleep(0.5)

        return location

    def context_click(self, step):
        actions = ActionChains(self.driver)
        location = self.locat(step['element'])
        actions.context_click(location)
        actions.perform()
        sleep(0.5)

        return location

    def double_click(self, step):
        actions = ActionChains(self.driver)
        location = self.locat(step['element'])
        actions.double_click(location)
        actions.perform()
        sleep(0.5)

        return location

    def drag_and_drop(self, step):
        actions = ActionChains(self.driver)
        elements = step['elements']
        source = self.locat(elements[0])
        target = self.locat(elements[1])
        actions.drag_and_drop(source, target)
        actions.perform()
        sleep(0.5)

    def swipe(self, step):
        actions = ActionChains(self.driver)
        data = step['data']
        location = self.locat(step['element'])
        x = data.get('x', 0)
        y = data.get('y', 0)
        actions.drag_and_drop_by_offset(location, x, y)
        actions.perform()
        sleep(0.5)

    def script(self, step):
        element = step['element']
        self.driver.execute_script(element)

    def message(self, step):
        data = step['data']
        text = data.get('text', '')
        value = step['element']

        if value.lower() in ('确认', 'accept'):
            self.driver.switch_to_alert().accept()
        elif value.lower() in ('取消', '关闭', 'cancel', 'close'):
            self.driver.switch_to_alert().dismiss()
        elif value.lower() in ('输入', 'input'):
            self.driver.switch_to_alert().send_keys(text)
            self.driver.switch_to_alert().accept()
        log.debug('switch frame: Alert')
        self.w.frame = 'Alert'

    def upload(self, step):
        import win32com.client

        data = step['data']
        location = self.locat(step['element'])
        file_path = data.get('text', '') or data.get('file', '')

        location.click()
        sleep(3)
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.Sendkeys(file_path)
        sleep(2)
        shell.Sendkeys("{ENTER}")
        sleep(2)

    def navigate(self, step):
        element = step['element']

        if element.lower() in ('刷新', 'refresh'):
            self.driver.refresh()
        elif element.lower() in ('前进', 'forward'):
            self.driver.forward()
        elif element.lower() in ('后退', 'back'):
            self.driver.back()

    def scroll(self, step):
        data = step['data']
        x = data.get('x')
        y = data.get('y') or data.get('text')

        element = step['element']
        if element == '':
            # if x is None:
            #     x = '0'
            # self.driver.execute_script(
            #     f"windoself.w.scrollTo({x},{y})")
            if y:
                self.driver.execute_script(
                    f"document.documentElement.scrollTop={y}")
            if x:
                self.driver.execute_script(
                    f"document.documentElement.scrollLeft={x}")
        else:
            location = self.locat(element)

            if y:
                self.driver.execute_script(
                    f"arguments[0].scrollTop={y}", location)
            if x:
                self.driver.execute_script(
                    f"arguments[0].scrollLeft={x}", location)
