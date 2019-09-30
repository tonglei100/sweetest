from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException
from time import sleep
import re
from sweetest.globals import g
from sweetest.elements import e
from sweetest.windows import w
from sweetest.locator import locating_elements, locating_data, locating_element
from sweetest.log import logger
from sweetest.parse import data_format
from sweetest.utility import compare, json2dict


class Common():
    @classmethod
    def title(cls, data, output):
        logger.info('DATA:%s' % repr(data['text']))
        logger.info('REAL:%s' % repr(g.driver.title))
        try:
            if data['text'].startswith('*'):
                assert data['text'][1:] in g.driver.title
            else:
                assert data['text'] == g.driver.title
        except:
            raise Exception(f'Check Failure, DATA:{data["text"]}, REAL:{g.driver.title}')
        # 只能获取到元素标题
        for key in output:
            g.var[key] = g.driver.title
        return g.driver.title


    @classmethod
    def current_url(cls, data, output):
        logger.info('DATA:%s' % repr(data['text']))
        logger.info('REAL:%s' % repr(g.driver.current_url))
        try:
            if data['text'].startswith('*'):
                assert data['text'][1:] in g.driver.current_url
            else:
                assert data['text'] == g.driver.current_url
        except:
            raise Exception(f'Check Failure, DATA:{data["text"]}, REAL:{g.driver.current_url}')            
        # 只能获取到元素 url
        for key in output:
            g.var[key] = g.driver.current_url
        return g.driver.current_url


def open(step):
    element = step['element']
    value = e.get(element)[1]
    if step['data'].get('清理缓存', '') or step['data'].get('clear', ''):
        g.driver.delete_all_cookies()
    if step['data'].get('打开方式', '') == '新标签页' or step['data'].get('mode', '').lower() == 'tab':
        js = "window.open('%s')" % value
        g.driver.execute_script(js)
        # 判断是否打开了新的窗口，并将新窗口添加到所有窗口列表里
        all_handles = g.driver.window_handles
        for handle in all_handles:
            if handle not in w.windows.values():
                w.register(step, handle)
    else:
        if step['data'].get('打开方式', '') == '新浏览器' or step['data'].get('mode', '').lower() == 'browser':
            w.close()
            g.set_driver()
            w.init()
        g.driver.get(value)
        w.open(step)
    cookie = step['data'].get('cookie', '')
    if cookie:
        g.driver.add_cookie(json2dict(cookie))
        co = g.driver.get_cookie(json2dict(cookie).get('name', ''))
        logger.info(f'cookie is add: {co}')
    sleep(0.5)


def check(step):
    data = step['data']
    if not data:
        data = step['expected']

    element = step['element']
    element_location = locating_element(element)
    if '#' in element:
        e_name = element.split('#')[0] + '#'
    else:
        e_name = element
    by = e.elements[e_name]['by']
    output = step['output']
    var = {}

    if by in ('title', 'current_url'):
        var[by] = getattr(Common, by)(data, output)

    else:
        for key in data:
            # 预期结果
            expected = data[key]
            # 切片操作处理
            s = re.findall(r'\[.*?\]', key)
            if s:
                s = s[0]
                key = key.replace(s, '')

            if key == 'text':
                real = element_location.text
            else:
                real = element_location.get_attribute(key)
            if s:
                real = eval('real' + s)

            logger.info('DATA:%s' % repr(expected))
            logger.info('REAL:%s' % repr(real))
            try:
                compare(expected, real)
            except:
                raise Exception(f'Check Failure, DATA:{repr(expected)}, REAL:{repr(real)}')

        # 获取元素其他属性
        for key in output:
            if output[key] == 'text':
                var[key] = g.var[key] = element_location.text
            elif output[key] in ('text…', 'text...'):
                if element_location.text.endswith('...'):
                    var[key] = g.var[key] = element_location.text[:-3]
                else:
                    var[key] = g.var[key] = element_location.text
            else:
                var[key] = g.var[key] = element_location.get_attribute(output[key])
    if var:
        step['_output'] += '||output=' + str(var)
    return element_location


def notcheck(step):
    data = step['data']
    if not data:
        data = step['expected']

    element = step['element']
    # element_location = locating_element(element)

    if e.elements[element]['by'] == 'title':
        assert data['text'] != g.driver.title


def input(step):
    data = step['data']
    element = step['element']
    element_location = locating_element(element)

    if step['data'].get('清除文本', '') == '否' or step['data'].get('clear', '').lower() == 'no':
        pass
    else:
        element_location.clear()

    for key in data:
        if key.startswith('text'):
            if isinstance(data[key], tuple):
                element_location.send_keys(*data[key])
            elif element_location:
                element_location.send_keys(data[key])
            sleep(0.5)
        if key == 'word':  #逐字输入
            for d in data[key]:
                element_location.send_keys(d)
                sleep(0.3)
    return element_location


def click(step):
    element = step['element']
    data = step['data']
    if isinstance(element, str):
        element_location = locating_element(element, 'CLICK')
        if element_location:
            try:
                element_location.click()
            except ElementClickInterceptedException:  # 如果元素为不可点击状态，则等待1秒，再重试一次
                sleep(1)
                if data.get('mode'):
                    g.driver.execute_script("arguments[0].click();", element_location)
                else:
                    element_location.click()
    elif isinstance(element, list):
        for _e in element:
            element_location = locating_element(_e, 'CLICK')
            try:
                element_location.click()
            except ElementClickInterceptedException:  # 如果元素为不可点击状态，则等待1秒，再重试一次
                sleep(1)
                if data.get('mode'):
                    g.driver.execute_script("arguments[0].click();", element_location)
                else:
                    element_location.click()        
            sleep(0.5)
    sleep(0.5)

    # 获取元素其他属性
    output = step['output']
    for key in output:
        if output[key] == 'text':
            g.var[key] = element_location.text
        elif output[key] in ('text…', 'text...'):
            if element_location.text.endswith('...'):
                g.var[key] = element_location.text[:-3]
            else:
                g.var[key] = element_location.text
        else:
            g.var[key] = element_location.get_attribute(output[key])

    # 判断是否打开了新的窗口，并将新窗口添加到所有窗口列表里
    all_handles = g.driver.window_handles
    for handle in all_handles:
        if handle not in w.windows.values():
            w.register(step, handle)

    return element_location


def select(step):
    pass


def hover(step):
    actions = ActionChains(g.driver)
    element = step['element']
    element_location = locating_element(element)
    actions.move_to_element(element_location)
    actions.perform()
    sleep(0.5)

    return element_location


def context_click(step):
    actions = ActionChains(g.driver)
    element = step['element']
    element_location = locating_element(element)
    actions.context_click(element_location)
    actions.perform()
    sleep(0.5)

    return element_location


def double_click(step):
    actions = ActionChains(g.driver)
    element = step['element']
    element_location = locating_element(element)
    actions.double_click(element_location)
    actions.perform()
    sleep(0.5)

    return element_location


def drag_and_drop(step):
    actions = ActionChains(g.driver)
    element = step['element']
    source = locating_element(element[0])
    target = locating_element(element[1])
    actions.drag_and_drop(source, target)
    actions.perform()
    sleep(0.5)


def swipe(step):
    actions = ActionChains(g.driver)
    element = step['element']
    data = step['data']

    source = locating_element(element)
    x = data.get('x', 0)
    y = data.get('y', 0)
    actions.drag_and_drop_by_offset(source, x, y)
    actions.perform()
    sleep(0.5)


def script(step):
    element = step['element']
    value = e.get(element)[1]
    g.driver.execute_script(value)


def message(step):
    data = step['data']
    text = data.get('text', '')
    element = step['element']
    value = e.get(element)[1]

    if value.lower() in ('确认', 'accept'):
        g.driver.switch_to_alert().accept()
    elif value.lower() in ('取消', '关闭', 'cancel', 'close'):
        g.driver.switch_to_alert().dismiss()
    elif value.lower() in ('输入', 'input'):
        g.driver.switch_to_alert().send_keys(text)
        g.driver.switch_to_alert().accept()
    logger.info('--- Switch Frame: Alert')
    w.frame = 'Alert'


def upload(step):
    import win32com.client

    data = step['data']
    element = step['element']
    element_location = locating_element(element)
    file_path = data.get('text', '') or data.get('file', '')

    element_location.click()
    sleep(3)
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.Sendkeys(file_path)
    sleep(2)
    shell.Sendkeys("{ENTER}")
    sleep(2)


def navigate(step):
    element = step['element']

    if element.lower() in ('刷新', 'refresh'):
        g.driver.refresh()
    elif element.lower() in ('前进', 'forward'):
        g.driver.forward()
    elif element.lower() in ('后退', 'back'):
        g.driver.back()


def scroll(step):
    data = step['data']
    x = data.get('x')
    y = data.get('y') or data.get('text')

    element = step['element']
    if element == '':
        # if x is None:
        #     x = '0'
        # g.driver.execute_script(
        #     f"window.scrollTo({x},{y})")
        if y:
            g.driver.execute_script(
                f"document.documentElement.scrollTop={y}")
        if x:
            g.driver.execute_script(
                f"document.documentElement.scrollLeft={x}")         
    else:
        element_location = locating_element(element)

        if y:
            g.driver.execute_script(
                f"arguments[0].scrollTop={y}", element_location)
        if x:
            g.driver.execute_script(
                f"arguments[0].scrollLeft={x}", element_location)               