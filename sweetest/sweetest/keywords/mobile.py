from time import sleep
import re
from sweetest.globals import g
from sweetest.elements import e
from sweetest.windows import w
from sweetest.locator import locating_elements, locating_data, locating_element
from sweetest.log import logger
from sweetest.parse import data_format
from sweetest.utility import str2int, str2float
from appium.webdriver.common.touch_action import TouchAction


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
                real = eval('real'+s)
            logger.info('DATA:%s' % repr(expected))
            logger.info('REAL:%s' % repr(real))
            if isinstance(expected, str):
                if expected.startswith('*'):
                    assert expected[1:] in real
                else:
                    assert expected == real
            elif isinstance(expected, int):
                real = str2int(real)
                assert real == round(expected)
            elif isinstance(expected, float):
                t, p1 = str2float(real)
                d, p2 = str2float(expected)
                p = min(p1, p2)
                assert round(t, p) == round(d, p)
            elif expected is None:
                assert real == ''

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
    element_location = locating_element(element)

    if e.elements[element]['by'] == 'title':
        assert data['text'] != g.driver.title


def input(step):
    data = step['data']
    element = step['element']
    element_location = locating_element(element, text=data['text'])

    if isinstance(data['text'], tuple):
        element_location.send_keys(*data['text'])
    elif element_location:
        if step['data'].get('清除文本', '') == '否' or step['data'].get('clear', '').lower() == 'no':
            pass
        else:
            element_location.clear()
        element_location.send_keys(data['text'])


def set_value(step):
    data = step['data']
    element = step['element']
    element_location = locating_element(element, text=data['text'])

    if isinstance(data['text'], tuple):
        element_location.set_value(*data['text'])
    elif element_location:
        if step['data'].get('清除文本', '') == '否' or step['data'].get('clear', '').lower() == 'no':
            pass
        else:
            element_location.clear()
        element_location.set_value(data['text'])


def click(step):
    element = step['element']
    if isinstance(element, str):
        element_location = locating_element(element, 'CLICK')
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
        elif output[key] == 'tag_name':
            g.var[key] = element_location.tag_name
        elif output[key] in ('text…', 'text...'):
            if element_location.text.endswith('...'):
                g.var[key] = element_location.text[:-3]
            else:
                g.var[key] = element_location.text
        else:
            g.var[key] = element_location.get_attribute(output[key])


def tap(step):
    action = TouchAction(g.driver)

    element = step['element']
    if isinstance(element, str):
        if '(' in element and ')' in element:
            positions = eval(element)
            g.driver.tap([positions])
        else:
            element_location = locating_element(element, 'CLICK')
            action.tap(element_location).perform()
    elif isinstance(element, list):
        if '(' in element[0] and ')' in element[0]:
            positions = [eval(_e) for _e in element]
            g.driver.tap([position])
        else:
            for _e in element:
                element_location = locating_element(_e, 'CLICK')
                action.tap(element_location).perform()
                sleep(0.5)
    sleep(0.5)

    # 获取元素其他属性
    output = step['output']
    for key in output:
        if output[key] == 'text':
            g.var[key] = element_location.text
        elif output[key] == 'tag_name':
            g.var[key] = element_location.tag_name
        elif output[key] in ('text…', 'text...'):
            if element_location.text.endswith('...'):
                g.var[key] = element_location.text[:-3]
            else:
                g.var[key] = element_location.text
        else:
            g.var[key] = element_location.get_attribute(output[key])


def press_keycode(step):
    element = step['element']
    g.driver.press_keycode(int(element))


def swipe(step):
    element = step['element']
    duration = step['data'].get('持续时间', 0.3)
    assert isinstance(element, list) and len(element) == 4, '坐标格式或数量不对，正确格式如：100|200|300|400'
    start_x = eval(element[0])
    start_y = eval(element[1])
    end_x = eval(element[2])
    end_y = eval(element[3])
    if duration:
        g.driver.swipe(start_x, start_y, end_x, end_y, sleep(int(duration)))
    else:
        g.driver.swipe(start_x, start_y, end_x, end_y)


def scroll(step):
    element = step['element']
    assert isinstance(element, list) and len(element) == 2, '元素格式或数量不对，正确格式如：origin_el|destination_el'
    origin = locating_element(element[0])
    destination = locating_element(element[1])
    g.driver.scroll(origin, destination)


def flick_element(step):
    element = step['element']
    speed = step['data'].get('持续时间', 10)
    assert isinstance(element, list) and len(element) == 3, '坐标格式或数量不对，正确格式如：elment|200|300'
    _e = eval(element[0])
    end_x = eval(element[2])
    end_y = eval(element[3])
    if speed:
        g.driver.flick_element(_e, end_x, end_y, int(speed))


def flick(step):
    element = step['element']
    assert isinstance(element, list) and len(element) == 4, '坐标格式或数量不对，正确格式如：100|200|300|400'
    start_x = eval(element[0])
    start_y = eval(element[1])
    end_x = eval(element[2])
    end_y = eval(element[3])
    g.driver.flick(start_x, start_y, end_x, end_y)


def drag_and_drop(step):
    element = step['element']
    assert isinstance(element, list) and len(element) == 2, '元素格式或数量不对，正确格式如：origin_el|destination_el'
    origin = locating_element(element[0])
    destination = locating_element(element[1])
    g.driver.drag_and_drop(origin, destination)


def long_press(step):
    action = TouchAction(g.driver)

    element = step['element']
    duration = step['data'].get('持续时间', 1000)
    if isinstance(element, str):
        element_location = locating_element(element)
        action.long_press(element_location, duration=duration).perform()
    elif isinstance(element, list):
        assert isinstance(element, list) and len(element) == 2, '元素格式或数量不对，正确格式如：100|200'
        action.long_press(x=int(element[0]), y=int(element[1]), duration=duration).perform()
    sleep(0.5)


def pinch(step):
    element = step['element']
    element_location = locating_element(element[0])
    percent = step['data'].get('百分比', 200)
    steps = step['data'].get('步长', 50)
    g.driver.pinch(element_location, percent, steps)


def zoom(step):
    element = step['element']
    element_location = locating_element(element[0])
    percent = step['data'].get('百分比', 200)
    steps = step['data'].get('步长', 50)
    g.driver.zoom(element_location, percent, steps)


def hide_keyboard(step):
    g.driver.hide_keyboard()


def shake(step):
    g.driver.shake()
