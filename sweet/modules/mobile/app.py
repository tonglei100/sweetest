from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
from appium.webdriver.common.touch_action import TouchAction
from time import sleep
import re

from sweet import log, vars
from sweet.utility import compare, replace, json2dict

from sweet.modules.mobile.window import Windows
from sweet.modules.web.locator import locating
from sweet.modules.web.config import *


class App:

    keywords = keywords

    def __init__(self, setting):
        self.action = {}
        platform = setting.get('platformName', '')
        # snapshot = setting.pop('snapshot', False)

        if platform.lower() == 'ios':
            from appium import webdriver as appdriver
            self.driver = appdriver.Remote(self.server_url, self.desired_caps)

        elif platform.lower() == 'android':
            from appium import webdriver as appdriver
            self.driver = appdriver.Remote(self.server_url, self.desired_caps)

        # 等待元素超时时间
        self.driver.implicitly_wait(element_wait_timeout)  # seconds
        # 页面刷新超时时间
        self.driver.set_page_load_timeout(page_flash_timeout)  # seconds
        self.w = Windows()
        self.w.driver = self.driver

    def _close(self):
        pass

    def _call(self, step):
        # 处理截图数据
        # snap = Snapshot()
        # snap.pre(step)

        context = replace(step.get('frame', '')).strip()
        self.w.switch_context(context)

        if self.w.current_context.startswith('WEBVIEW'):
            # 切换标签页
            tab = step['data'].get('#tab')
            if tab:
                del step['data']['#tab']
                self.driver.switch_to_window(self.w.windows[tab])
            log.debug(f'current context: {repr(self.w.current_context)}')

        # 根据关键字调用关键字实现
        element = getattr(self, step['keyword'].lower())(step)
        # snap.web_shot(step, element)


    def title(self, data, output):
        log.debug(f'DATA:{repr(data["text"])}')
        log.debug(f'REAL:{repr(self.driver.title)}')

        if data['text'].startswith('*'):
            assert data['text'][1:] in self.driver.title
        else:
            assert data['text'] == self.driver.title
        # 只能获取到元素标题
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
        return self.driver.current_url

    def locat(self, element, action=''):
        if not isinstance(element, dict):
            raise Exception(f'no this element:{element}')


    def open(self, step):
        url = step['element']['value']

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
                log.debug(f'REAL:{repr(real)}')
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

    def set_value(self, step):
        data = step['data']
        location = self.locat(step['element'])
        if step['data'].get('清除文本', '') == '否' or step['data'].get('clear', '').lower() == 'no':
            pass
        else:
            location.clear()

        for key in data:
            if key.startswith('text'):
                if isinstance(data[key], tuple):
                    location.set_value(*data[key])
                elif location:
                    location.set_value(data[key])
                sleep(0.5)
            if key == 'word':  # 逐字输入
                for d in data[key]:
                    location.set_value(d)
                    sleep(0.3)

    def click(self, step):
        elements = step['elements']  # click 支持多个元素连续操作，需要转换为 list
        # data = step['data']

        location = ''
        for element in elements:
            location = self.locat(element, 'CLICK')
            sleep(0.5)
            try:
                location.click()
            except ElementClickInterceptedException:  # 如果元素为不可点击状态，则等待1秒，再重试一次
                sleep(1)
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

    def tap(self, step):
        action = TouchAction(self.driver)

        elements = step['elements']  # click 支持多个元素连续操作，需要转换为 list
        # data = step['data']

        location = ''

        for element in elements:
            if ',' in element:
                position = element.split(',')
                x = int(position[0])
                y = int(position[1])
                position = (x, y)
                self.driver.tap([position])
                sleep(0.5)
            else:
                location = self.locat(element, 'CLICK')
                action.tap(location).perform()
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

    def press_keycode(self, step):
        element = step['element']
        self.driver.press_keycode(int(element))

    def swipe(self, step):
        elements = step['elements']
        duration = step['data'].get('持续时间', 0.3)
        assert isinstance(elements, list) and len(
            elements) == 2, '坐标格式或数量不对，正确格式如：100,200|300,400'

        start = elements[0].replace('，', ',').split(',')
        start_x = int(start[0])
        start_y = int(start[1])

        end = elements[1].replace('，', ',').split(',')
        end_x = int(end[0])
        end_y = int(end[1])

        if duration:
            self.driver.swipe(start_x, start_y, end_x,
                              end_y, sleep(float(duration)))
        else:
            self.driver.swipe(start_x, start_y, end_x, end_y)

    def line(self, step):
        elements = step['elements']
        duration = float(step['data'].get('持续时间', 0.3))
        assert isinstance(elements, list) and len(
            elements) > 1, '坐标格式或数量不对，正确格式如：258,756|540,1032'
        postions = []
        for element in elements:
            element = element.replace('，', ',')
            p = element.split(',')
            postions.append(p)

        action = TouchAction(self.driver)
        action = action.press(
            x=postions[0][0], y=postions[0][1]).wait(duration * 1000)
        for i in range(1, len(postions)):
            action.move_to(x=postions[i][0], y=postions[i]
                           [1]).wait(duration * 1000)
        action.release().perform()

    def line_unlock(self, step):
        elements = step['elements']
        duration = float(step['data'].get('持续时间', 0.3))
        assert isinstance(elements, list) and len(
            elements) > 2, '坐标格式或数量不对，正确格式如：lock_pattern|1|4|7|8|9'
        location = self.locat(elements[0]) 
        rect = location.rect
        w = rect['width'] / 6
        h = rect['height'] / 6

        key = {}
        key['1'] = (rect['x'] + 1 * w, rect['y'] + 1 * h)
        key['2'] = (rect['x'] + 3 * w, rect['y'] + 1 * h)
        key['3'] = (rect['x'] + 5 * w, rect['y'] + 1 * h)
        key['4'] = (rect['x'] + 1 * w, rect['y'] + 3 * h)
        key['5'] = (rect['x'] + 3 * w, rect['y'] + 3 * h)
        key['6'] = (rect['x'] + 5 * w, rect['y'] + 3 * h)
        key['7'] = (rect['x'] + 1 * w, rect['y'] + 5 * h)
        key['8'] = (rect['x'] + 3 * w, rect['y'] + 5 * h)
        key['9'] = (rect['x'] + 5 * w, rect['y'] + 5 * h)

        action = TouchAction(self.driver)
        for i in range(1, len(elements)):
            k = elements[i]
            if i == 1:
                action = action.press(
                    x=key[k][0], y=key[k][1]).wait(duration * 1000)
            action.move_to(x=key[k][0], y=key[k][1]).wait(duration * 1000)
        action.release().perform()

    def rocker(self, step):
        elements = step['elements']
        duration = float(step['data'].get('持续时间', 0.3))
        rocker_name = step['data'].get('摇杆', 'rocker')
        release = step['data'].get('释放', False)

        # if isinstance(element, str):
        #     if element:
        #         element = [element]
        #     else:
        #         element = []

        postions = []
        for element in elements:
            element = element.replace('，', ',')
            p = element.split(',')
            postions.append(p)

        # 如果 action 中么有此摇杆名，则是新的遥感
        if not self.action.get(rocker_name):
            self.action[rocker_name] = TouchAction(self.driver)
            self.action[rocker_name].press(
                x=postions[0][0], y=postions[0][1]).wait(duration * 1000)
            # 新摇杆的第一个点已操作，需要删除
            postions.pop(0)
        # 依次操作
        for i in range(len(postions)):
            self.action[rocker_name].move_to(
                x=postions[i][0], y=postions[i][1]).wait(duration * 1000)

        if release:
            # 释放摇杆，并删除摇杆
            self.action[rocker_name].release().perform()
            del self.action[rocker_name]
        else:
            self.action[rocker_name].perform()

    def scroll(self, step):
        elements = step['elements']
        assert isinstance(elements, list) and len(
            elements) == 2, '元素格式或数量不对，正确格式如：origin_el|destination_el'
        origin = self.locat(elements[0])
        destination = self.locat(elements[1])
        self.driver.scroll(origin, destination)

    def flick_element(self, step):
        elements = step['elements']
        speed = step['data'].get('持续时间', 10)
        assert isinstance(elements, list) and len(
            elements) == 2, '坐标格式或数量不对，正确格式如：elment|200,300'
        location = self.locat(elements[0])

        end = elements[1].replace('，', ',').split(',')
        end_x = int(end[0])
        end_y = int(end[1])

        if speed:
            self.driver.flick_element(location, end_x, end_y, int(speed))

    def flick(self, step):
        elements = step['elements']
        assert isinstance(elements, list) and len(
            elements) == 2, '坐标格式或数量不对，正确格式如：100,200|300,400'

        start = elements[0].replace('，', ',').split(',')
        start_x = int(start[0])
        start_y = int(start[1])

        end = elements[1].replace('，', ',').split(',')
        end_x = int(end[0])
        end_y = int(end[1])

        self.driver.flick(start_x, start_y, end_x, end_y)

    def drag_and_drop(self, step):
        elements = step['elements']
        assert isinstance(elements, list) and len(
            elements) == 2, '元素格式或数量不对，正确格式如：origin_el|destination_el'
        origin = self.locat(elements[0])
        destination = self.locat(elements[1])        
        self.driver.drag_and_drop(origin, destination)

    def long_press(self, step):
        action = TouchAction(self.driver)

        element = step['element']
        duration = step['data'].get('持续时间', 1000)
        if ',' in element or '，' in element:
            position = element.replace('，', ',').split(',')
            x = int(position[0])
            y = int(position[1])
            action.long_press(x=x, y=y, duration=duration).perform()
        else:
            location = self.locat(element)
            action.long_press(location, duration=duration).perform()
        sleep(0.5)

    def pinch(self, step):
        element = step['element']
        location = self.locat(element)
        percent = step['data'].get('百分比', 200)
        steps = step['data'].get('步长', 50)
        self.driver.pinch(location, percent, steps)

    def zoom(self, step):
        element = step['element']
        location = self.locat(element)
        percent = step['data'].get('百分比', 200)
        steps = step['data'].get('步长', 50)
        self.driver.zoom(location, percent, steps)

    def hide_keyboard(self, step):
        self.driver.hide_keyboard()

    def shake(self, step):
        self.driver.shake()

    def launch_app(self, step):
        self.driver.launch_app()

    def is_locked(self, step):
        status = self.driver.is_locked()
        assert status, "it's not locked"

    def lock(self, step):
        self.driver.lock()

    def unlock(self, step):
        self.driver.unlock()