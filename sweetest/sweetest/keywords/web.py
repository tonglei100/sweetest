from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import re
from sweetest.globals import g
from sweetest.elements import e
from sweetest.windows import w
from sweetest.locator import locating_elements, locating_data, locating_element
from sweetest.log import logger
from sweetest.parse import data_format
from sweetest.utility import compare


class Common():
    @classmethod
    def title(cls, data, output):
        logger.info('DATA:%s' % repr(data['text']))
        logger.info('REAL:%s' % repr(g.driver.title))
        if data['text'].startswith('*'):
            assert data['text'][1:] in g.driver.title
        else:
            assert data['text'] == g.driver.title
        # 只能获取到元素标题
        for key in output:
            g.var[key] = g.driver.title

    @classmethod
    def current_url(cls, data, output):
        logger.info('DATA:%s' % repr(data['text']))
        logger.info('REAL:%s' % repr(g.driver.current_url))
        if data['text'].startswith('*'):
            assert data['text'][1:] in g.driver.current_url
        else:
            assert data['text'] == g.driver.current_url
        # 只能获取到元素 url
        for key in output:
            g.var[key] = g.driver.current_url


def open(step):
    element = step['element']
    value = e.get(element)[1]
    if step['data'].get('清理缓存', '') or step['data'].get('cookie', ''):
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

    if by in ('title', 'current_url'):
        getattr(Common, by)(data, output)

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
            compare(expected, real)

        # 获取元素其他属性
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


def click(step):
    element = step['element']
    if isinstance(element, str):
        element_location = locating_element(element, 'CLICK')
        if element_location:
            element_location.click()
    elif isinstance(element, list):
        for _e in element:
            element_location = locating_element(_e, 'CLICK')
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


def select(step):
    pass


def move(step):
    actions = ActionChains(g.driver)
    element = step['element']
    el = locating_element(element)
    actions.move_to_element(el)
    actions.perform()
    sleep(0.5)


def context_click(step):
    actions = ActionChains(g.driver)
    element = step['element']
    el = locating_element(element)
    actions.context_click(el)
    actions.perform()
    sleep(0.5)


def double_click(step):
    actions = ActionChains(g.driver)
    element = step['element']
    el = locating_element(element)
    actions.double_click(el)
    actions.perform()
    sleep(0.5)


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


def refresh(step):
    g.driver.refresh()
