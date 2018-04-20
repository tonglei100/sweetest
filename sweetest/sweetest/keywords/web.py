from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from sweetest.globals import g
from sweetest.elements import e
from sweetest.windows import w
from sweetest.locator import locating_elements, locating_data, locating_element
from sweetest.log import logger
from sweetest.parse import data_format
from sweetest.utility import str2int, str2float


class Common():
    @classmethod
    def title(cls, data, output):
        logger.info('DATA:%s' % repr(data['text']))
        logger.info('REAL: %s' % repr(g.driver.title))
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
        logger.info('REAL: %s' % repr(g.driver.current_url))
        if data['text'].startswith('*'):
            assert data['text'][1:] in g.driver.current_url
        else:
            assert data['text'] == g.driver.current_url
        # 只能获取到元素 url
        for key in output:
            g.var[key] = g.driver.current_url


def open(step):
    element = step['element']
    el, value = e.get(element)
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
            if key == 'text':
                text = element_location.text
                logger.info('DATA:%s' % repr(data[key]))
                logger.info('REAL: %s' % repr(text))
                if data[key].startswith('*'):
                    assert data[key][1:] in text
                else:
                    if isinstance(data[key], int):
                        text = str2int(text)
                        assert text == round(data[key])
                    elif isinstance(data[key], float):
                        t, p1 = str2float(text)
                        d, p2 = str2float(data[key])
                        p = min(p1, p2)
                        assert round(t, p) == round(d, p)
                    else:
                        assert data[key] == text
            else:
                logger.info('DATA:%s' % repr(data[key]))
                logger.info('REAL: %s' % repr(element_location.get_attribute(key)))
                if data[key].startswith('*'):
                    assert data[key][1:] in element_location.get_attribute(key)
                else:
                    vaule = element_location.get_attribute(key)
                    if isinstance(data[key], int):
                        vaule = str2int(vaule)
                        assert text == round(data)
                    elif isinstance(data[key], float):
                        t, p1 = str2float(text)
                        d, p2 = str2float(data[key])
                        p = min(p1, p2)
                        assert round(t, p) == round(d, p)
                    else:
                        assert data[key] == vaule

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
    element_location = locating_element(element)

    element_location.clear()
    element_location.send_keys(data['text'])


def click(step):
    element = step['element']
    element_location = locating_element(element, 'CLICK')
    element_location.click()
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
