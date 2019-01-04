from time import sleep
import re
from sweetest.globals import g
from sweetest.elements import e
from sweetest.windows import w
from sweetest.locator import locating_elements, locating_data, locating_element
from sweetest.log import logger
from sweetest.parse import data_format
from sweetest.utility import compare
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
    element_location = locating_element(element)

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
        #element_location = locating_element(element, 'CLICK')
        element_location = locating_element(element)
        element_location.click()
    elif isinstance(element, list):
        for _e in element:
            #element_location = locating_element(_e, 'CLICK')
            element_location = locating_element(_e)
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

    # if w.current_context.startswith('WEBVIEW'):
    #     # 判断是否打开了新的窗口，并将新窗口添加到所有窗口列表里
    #     all_handles = g.driver.window_handles
    #     for handle in all_handles:
    #         if handle not in w.windows.values():
    #             w.register(step, handle)


def tap(step):
    action = TouchAction(g.driver)

    element = step['element']
    if isinstance(element, str):

        if ',' in element or '，' in element:
            position = element.replace('，', ',').split(',')
            x = int(position[0])
            y = int(position[1])
            position = (x,y)
            g.driver.tap([position])
        else:
            element_location = locating_element(element, 'CLICK')
            action.tap(element_location).perform()
    elif isinstance(element, list):
        if ',' in element[0] or '，' in element[0]:
            positions = [eval('('+ _e + ')') for _e in element]
            g.driver.tap([positions])
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

    # if w.current_context.startswith('WEBVIEW'):
    #     # 判断是否打开了新的窗口，并将新窗口添加到所有窗口列表里
    #     all_handles = g.driver.window_handles
    #     for handle in all_handles:
    #         if handle not in w.windows.values():
    #             w.register(step, handle)


def press_keycode(step):
    element = step['element']
    g.driver.press_keycode(int(element))


def swipe(step):
    element = step['element']
    duration = step['data'].get('持续时间', 0.3)
    assert isinstance(element, list) and len(element) == 2, '坐标格式或数量不对，正确格式如：100,200|300,400'

    start = element[0].replace('，', ',').split(',')
    start_x = int(start[0])
    start_y = int(start[1])

    end = element[1].replace('，', ',').split(',')
    end_x = int(end[0])
    end_y = int(end[1])

    if duration:
        g.driver.swipe(start_x, start_y, end_x, end_y, sleep(float(duration)))
    else:
        g.driver.swipe(start_x, start_y, end_x, end_y)


def line(step):
    element = step['element']
    duration = float(step['data'].get('持续时间', 0.3))
    assert isinstance(element, list) and len(element) > 1, '坐标格式或数量不对，正确格式如：258,756|540,1032'
    postions = []
    for _e in element:
        _e = _e.replace('，', ',')
        p = _e.split(',')
        postions.append(p)

    action = TouchAction(g.driver)
    action = action.press(x=postions[0][0], y=postions[0][1]).wait(duration*1000)
    for i in range(1, len(postions)):
        action.move_to(x=postions[i][0], y=postions[i][1]).wait(duration*1000)
    action.release().perform()


def line_unlock(step):
    element = step['element']
    duration = float(step['data'].get('持续时间', 0.3))
    assert isinstance(element, list) and len(element) > 2, '坐标格式或数量不对，正确格式如：lock_pattern|1|4|7|8|9'
    _e = locating_element(element[0])
    rect = _e.rect
    w = rect['width']/6
    h = rect['height']/6

    key = {}
    key['1'] = (rect['x'] + 1*w, rect['y'] + 1*h)
    key['2'] = (rect['x'] + 3*w, rect['y'] + 1*h)
    key['3'] = (rect['x'] + 5*w, rect['y'] + 1*h)
    key['4'] = (rect['x'] + 1*w, rect['y'] + 3*h)
    key['5'] = (rect['x'] + 3*w, rect['y'] + 3*h)
    key['6'] = (rect['x'] + 5*w, rect['y'] + 3*h)
    key['7'] = (rect['x'] + 1*w, rect['y'] + 5*h)
    key['8'] = (rect['x'] + 3*w, rect['y'] + 5*h)
    key['9'] = (rect['x'] + 5*w, rect['y'] + 5*h)

    action = TouchAction(g.driver)
    for i in range(1, len(element)):
        k = element[i]
        if i == 1:
            action = action.press(x=key[k][0], y=key[k][1]).wait(duration*1000)
        action.move_to(x=key[k][0], y=key[k][1]).wait(duration*1000)
    action.release().perform()


def rocker(step):
    element = step['element']
    duration = float(step['data'].get('持续时间', 0.3))
    rocker_name = step['data'].get('摇杆', 'rocker')
    release = step['data'].get('释放', False)

    if isinstance(element, str):
        if element:
            element = [element]
        else:
            element = []

    postions = []
    for _e in element:
        _e = _e.replace('，', ',')
        p = _e.split(',')
        postions.append(p)

    # 如果 action 中么有此摇杆名，则是新的遥感
    if not g.action.get(rocker_name):
        g.action[rocker_name] = TouchAction(g.driver)
        g.action[rocker_name].press(x=postions[0][0], y=postions[0][1]).wait(duration*1000)
        # 新摇杆的第一个点已操作，需要删除
        postions.pop(0)
    # 依次操作
    for i in range(len(postions)):
        g.action[rocker_name].move_to(x=postions[i][0], y=postions[i][1]).wait(duration*1000)

    if release:
        # 释放摇杆，并删除摇杆
        g.action[rocker_name].release().perform()
        del g.action[rocker_name]
    else:
        g.action[rocker_name].perform()


def scroll(step):
    element = step['element']
    assert isinstance(element, list) and len(element) == 2, '元素格式或数量不对，正确格式如：origin_el|destination_el'
    origin = locating_element(element[0])
    destination = locating_element(element[1])
    g.driver.scroll(origin, destination)


def flick_element(step):
    element = step['element']
    speed = step['data'].get('持续时间', 10)
    assert isinstance(element, list) and len(element) == 2, '坐标格式或数量不对，正确格式如：elment|200,300'
    _e = eval(element[0])

    end = element[1].replace('，', ',').split(',')
    end_x = int(end[0])
    end_y = int(end[1])

    if speed:
        g.driver.flick_element(_e, end_x, end_y, int(speed))


def flick(step):
    element = step['element']
    assert isinstance(element, list) and len(element) == 2, '坐标格式或数量不对，正确格式如：100,200|300,400'

    start = element[0].replace('，', ',').split(',')
    start_x = int(start[0])
    start_y = int(start[1])

    end = element[1].replace('，', ',').split(',')
    end_x = int(end[0])
    end_y = int(end[1])

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
    if ',' in element or '，' in element:
        position = element.replace('，', ',').split(',')
        x = int(position[0])
        y = int(position[1])
        action.long_press(x=x, y=y, duration=duration).perform()
    else:
        element_location = locating_element(element)
        action.long_press(element_location, duration=duration).perform()
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


def tab_name(step):
    element = step['element']
    name = step['data']['text']
    # 从所有窗口中查找给定元素，如果查询到就命名，否则报错
    all_handles = g.driver.window_handles
    logger.info('All Handles: %s' % all_handles)

    flag = False
    for handle in all_handles:
        #logger.info('Page Source: %s \n%s' % (handle, g.driver.page_source))
        #logger.info('All Windows: %s' %w.windows)
        if handle not in w.windows.values():
            # 切换至此窗口
            g.driver.switch_to_window(handle)
            try:
                # 成功定位到关键元素
                element_location = locating_element(element, 'CLICK')
                # 添加到窗口资源池 g.windows
                w.windows[name] = handle
                # 把当前窗口名字改为新窗口名称
                w.current_window = name
                flag = True
                logger.info('Current Window: %s' % repr(name))
                logger.info('Current Handle: %s' % repr(handle))
            except Exception as exception:
                pass
    if not flag:
        raise Exception('Tab Name Fail: the element:%s in all tab is not found' %element)
