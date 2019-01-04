from copy import deepcopy
from sweetest.globals import g
from sweetest.elements import e
from sweetest.log import logger
from sweetest.parse import data_format
from sweetest.database import DB
from sweetest.utility import replace_dict, compare


def execute(step):
    # 先处理循环结束条件
    condition = ''
    for k in ('循环结束条件', 'condition'):
        if step['data'].get(k):
            condition = step['data'].get(k)
            del step['data'][k]
    if condition.lower() in ('成功', 'pass'):
        condition = 'Pass'
    elif condition.lower() in ('失败', 'fail'):
        condition = 'Fail'

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

    if len(_element) >= 2:
        element = _element[0]
        times = int(_element[1])

    # 初始化测试片段执行结果
    result = 'Pass'
    steps = []
    if element != '变量赋值':
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
                s['no'] = str(step['no']) + '*' + str(t+1) + '-' + str(s['no'])
            steps += testcase['steps']
            # 用例片段执行失败时
            if testcase['result'] != 'Pass':
                result = testcase['result']
                # 循环退出条件为失败，则直接返回，返回结果是 Pass
                if condition == 'Fail':
                    return 'Pass', testcase['steps']
                # 如果没有结束条件，且失败直接退出标志位真，则返回结果
                if not condition and flag:
                    return result, steps
            # 用例片段执行成功时
            else:
                # 如果循环退出条件是成功，则直接返回，返回结果是 Pass
                if condition == 'Pass':
                    return 'Pass', testcase['steps']
        # 执行结束，还没有触发循环退出条件，则返回结果为 Fail
        if condition:
            return 'Fail', testcase['steps']
        return result, steps


def sql(step):
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
        logger.info('SQL result: %s' % repr(row))
        if not row:
            raise Exception('*** Fetch None ***')
    else:
        g.db[step['page']].execute(_sql)

    result = {}
    if _sql.lower().startswith('select'):
        keys = _sql[6:].split('FROM')[0].split('from')[0].strip().split(',')
        for i,k in enumerate(keys):
            keys[i] = k.split(' ')[-1]
        result = dict(zip(keys, row))
        logger.info('keys result: %s' % repr(result))

    data = step['data']
    if not data:
        data = step['expected']
    if data:
        for key in data:
            sv, pv = data[key], result[key]
            logger.info('key: %s, expect: %s, real: %s' %
                        (repr(key), repr(sv), repr(pv)))

            compare(sv, pv)

    output = step['output']
    if output:
        logger.info('output: %s' % repr(output))
        for key in output:
            g.var[key] = result[output[key]]
