from copy import deepcopy
from sweetest.globals import g
from sweetest.elements import e
from sweetest.log import logger
from sweetest.parse import data_format
from sweetest.database import DB
from sweetest.utility import replace_dict, compare
from injson import check
from sweetest.utility import json2dict


def execute(step):
    # 先处理循环结束条件
    condition = ''
    for k in ('循环结束条件', 'condition', '#break'):
        if step['data'].get(k):
            condition = step['data'].get(k)
            del step['data'][k]
    if condition.lower() in ('成功', 'success'):
        condition = 'success'
    elif condition.lower() in ('失败', 'failure'):
        condition = 'failure'

    # 执行赋值操作
    data = step['data']
    for k, v in data.items():
        g.var[k] = v

    from sweetest.testcase import TestCase
    element = step['element']
    times = 1
    _element = element.split('*')

    # snippet 执行失败是否退出标志
    flag = True
    if element[-1] == '*':
        flag = False

    # 循环次数为 N 标志
    n_flag = False
    if len(_element) >= 2:
        element = _element[0]
        if _element[1].upper() == 'N':
            times = 999
            n_flag = True
        else:
            times = int(_element[1])
            
    # 初始化测试片段执行结果 
    result = 'success'
    steps = []
    testcase = {}
    if step['page'] in ('用例片段', 'SNIPPET'):
        g.var['_last_'] = False
        for t in range(times):
            if t > 0:
                _data = data_format(str(step['_data']))
                replace_dict(_data)
                for k, v in _data.items():
                    g.var[k] = v
            testcase = deepcopy(g.snippet[element])
            tc = TestCase(testcase)
            tc.run()
            for s in testcase['steps']:
                s['no'] = str(step['no']) + '*' + \
                    str(t + 1) + '-' + str(s['no'])
            steps += testcase['steps']
            # 用例片段执行失败时
            if testcase['result'] != 'success':
                result = testcase['result']
                # 循环退出条件为失败，则直接返回，返回结果是 success
                if condition == 'failure':
                    return 'success', testcase['steps']
                # 如果没有结束条件，且直接退出标志位为真，则返回结果
                if not condition and flag:
                    return result, steps

            # 用例片段执行成功时
            else:
                # 如果循环退出条件是成功，则直接返回，返回结果是 success
                if condition == 'success':
                    return 'success', testcase['steps']
            
            if n_flag and g.var['_last_']:  # 只有循环次数为 N 时，才判断是否是变量最后一个值
                g.var['_last_'] = False
                break
        # 执行结束，还没有触发循环退出条件，则返回结果为 failure
        if condition:
            return 'failure', testcase['steps']
    elif step['page'] in ('用例组合', 'CASESET'):
        caseset = element
        for t in range(times):
            if t > 0:
                _data = data_format(str(step['_data']))
                replace_dict(_data)
                for k, v in _data.items():
                    g.var[k] = v
            for testcase in g.caseset[caseset]:
                testcase = deepcopy(testcase)
                testcase['flag'] = ''
                g.ts.run_testcase(testcase)
                g.casesets.append(testcase)
                # if testcase['result'] != 'success':
                #     result = testcase['result']
    return result, steps


def dedup(text):
    '''
    去掉 text 中括号及其包含的字符
    '''
    _text = ''
    n = 0

    for s in text:
        if s not in ( '(', ')'):
            if n <= 0:
                _text += s
        elif s == '(':
            n += 1
        elif s == ')':
            n -= 1
    return _text    


def sql(step):

    response = {}

    element = step['element']
    _sql = e.get(element)[1]

    logger.info('SQL: %s' % repr(_sql))
    # 获取连接参数
    value = e.get(step['page'] + '-' + 'config')[1]
    arg = data_format(value)

    if step['page'] not in g.db.keys():
        g.db[step['page']] = DB(arg)
    if _sql.lower().startswith('select'):
        row = g.db[step['page']].fetchone(_sql)
        logger.info('SQL response: %s' % repr(row))
        if not row:
            raise Exception('*** Fetch None ***')
 
    elif _sql.lower().startswith('db.'):
        _sql_ = _sql.split('.', 2)
        collection = _sql_[1]
        sql = _sql_[2]
        response = g.db[step['page']].mongo(collection, sql)
        if response:
            logger.info('find result: %s' % repr(response))
    else:
        g.db[step['page']].execute(_sql)

    if _sql.lower().startswith('select'):
        text = _sql[6:].split('FROM')[0].split('from')[0].strip()
        keys = dedup(text).split(',')
        for i, k in enumerate(keys):
            keys[i] = k.split(' ')[-1]
        response = dict(zip(keys, row))
        logger.info('select result: %s' % repr(response))

    expected = step['data']
    if not expected:
        expected = step['expected']
    if 'json' in expected:
        expected['json'] = json2dict(expected.get('json', '{}'))
        result = check(expected.pop('json'), response['json'])
        logger.info('json check result: %s' % result)
        if result['code'] != 0:
            raise Exception(f'json | EXPECTED:{repr(expected["json"])}, REAL:{repr(response["json"])}, RESULT: {result}')
        elif result['var']:
            var = dict(var, **result['var'])
            g.var = dict(g.var, **result['var'])
            logger.info('json var: %s' % (repr(result['var']))) 

    if expected:
        for key in expected:
            sv, pv = expected[key], response[key]
            logger.info('key: %s, expect: %s, real: %s' %
                        (repr(key), repr(sv), repr(pv)))

            compare(sv, pv)

    output = step['output']
    if output:
        _output = {}
        for k, v in output.items():
            if k == 'json':
                sub = json2dict(output.get('json', '{}'))
                result = check(sub, response['json'])
                # logger.info('Compare json result: %s' % result)
                var = dict(var, **result['var'])
                g.var = dict(g.var, **result['var'])
                logger.info('json var: %s' % (repr(result['var'])))
            else:
                _output[k] = response[v]
                g.var[k] = response[v]
        logger.info('output: %s' % repr(_output))