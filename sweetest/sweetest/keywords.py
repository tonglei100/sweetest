from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from copy import deepcopy
from sweetest.globals import g
from sweetest.elements import e
from sweetest.windows import w
from sweetest.locator import locating_elements, locating_data, locating_element
from sweetest.log import logger
from sweetest.parse import data_format
from sweetest.database import DB

class Common():
    @classmethod
    def title(cls, data, output):
        logger.info('DATA:%s' %data['text'])
        logger.info('REAL: %s' %g.driver.title)
        if data['text'].startswith('*'):
            assert data['text'][1:] in g.driver.title
        else:
            assert data['text'] == g.driver.title
        # 只能获取到元素标题
        for key in output:
            g.var[key] = g.driver.title

    @classmethod
    def current_url(cls, data, output):
        logger.info('DATA:%s' %data['text'])
        logger.info('REAL: %s' %g.driver.current_url)
        if data['text'].startswith('*'):
            assert data['text'][1:] in g.driver.current_url
        else:
            assert data['text'] == g.driver.current_url
        # 只能获取到元素 url
        for key in output:
            g.var[key] = g.driver.current_url


def open(step):
    element = step['elements'][0]
    el, value = e.get(element)
    g.driver.get(value)
    w.open(step)
    sleep(0.5)


def check(step):
    data = step['data']
    element = step['elements'][0]
    element_location = locating_element(element)
    if '#' in element:
        e_name = element.split('#')[0] + '#'
    else:
        e_name = element
    by = e.elements[e_name]['by']
    output = step['output']

    if by in ('title','current_url'):
        getattr(Common, by)(data, output)

    else:
        for key in data:
            if key == 'text':
                logger.info('DATA:%s' %data[key])
                logger.info('REAL: %s' %element_location.text)
                if data[key].startswith('*'):
                    assert data[key][1:] in element_location.text
                else:
                    assert element_location.text == data[key]
            else:
                logger.info('DATA:%s' %data[key])
                logger.info('REAL: %s' %element_location.get_attribute(key))
                if data[key].startswith('*'):
                    assert data[key][1:] in element_location.get_attribute(key)
                else:
                    assert element_location.get_attribute(key) == data[key]
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
    element = step['elements'][0]
    element_location = locating_element(element)

    if e.elements[element]['by'] == 'title':
        assert data['text'] != g.driver.title


def input(step):
    data = step['data']
    elements_location = locating_elements(step['elements'])

    for element in elements_location:
        elements_location[element].clear()
        elements_location[element].send_keys(data['text'])


def click(step):
    element_location = ''
    for element in step['elements']:
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
    for element in step['elements']:
        el = locating_element(element)
        actions.move_to_element(el)
        actions.perform()
        sleep(0.5)


def execute(step):
    # 先执行赋值操作
    data = step['data']
    for k, v in data.items():
        g.var[k] = v

    from sweetest.testcase import TestCase
    for element in step['elements']:
        if element != '变量赋值':
            testcase = deepcopy(g.snippet[element])
            tc = TestCase(testcase)
            tc.run()


def sql(step):
    element = step['elements'][0]
    el, _sql = e.get(element)

    logger.info('SQL: %s' %_sql)
    # 获取连接参数
    el, value = e.get(step['page'] + '-' + '配置信息')
    arg = data_format(value)

    if step['page'] not in g.db.keys():
        g.db[step['page']] = DB(arg)
    row = g.db[step['page']].fetchone(_sql)
    logger.info('SQL result: %s' %(row,))

    result = {}
    if _sql.lower().startswith('select') and '*' not in _sql:
        keys = _sql[6:].split('FROM')[0].split('from')[0].strip().split(',')
        result = dict(zip(keys, row))
        logger.info('keys result: %s' %result)

    data = step['data']
    output = step['output']
    if data:
        for key in data:
            logger.info('key: %s, expect: %s, real: %s' %(key,data[key], result[key]))
            if data[key].startswith('*'):
                assert data[key][1:] in result[key]
            else:
                assert data[key] == result[key]

    if output:
        logger.info('output: %s' %output)
        for key in output:
            g.var[key] = result[output[key]]
