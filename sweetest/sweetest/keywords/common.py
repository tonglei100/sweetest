from copy import deepcopy
from sweetest.globals import g
from sweetest.elements import e
from sweetest.log import logger
from sweetest.parse import data_format
from sweetest.database import DB
from sweetest.utility import replace_dict


def execute(step):
    # 先执行赋值操作
    data = step['data']
    for k, v in data.items():
        g.var[k] = v

    from sweetest.testcase import TestCase
    element = step['element']
    times = 1
    _element = element.split('*')

    # snippet 执行失败是否退出标准
    flag = True
    if element[-1] == '*':
       flag = False

    if len(_element) >= 2:
        element = _element[0]
        times = int(_element[1])

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
                s['no'] = str(t+1) + '-' + str(s['no'])
            steps += testcase['steps']
            if testcase['result'] != 'Pass':
                if flag:
                    return steps
    return steps


def sql(step):
    element = step['element']
    el, _sql = e.get(element)

    logger.info('SQL: %s' % repr(_sql))
    # 获取连接参数
    el, value = e.get(step['page'] + '-' + 'config')
    arg = data_format(value)

    if step['page'] not in g.db.keys():
        g.db[step['page']] = DB(arg)
    row = g.db[step['page']].fetchone(_sql)
    logger.info('SQL result: %s' % repr(row))

    if not row:
        raise Exception('*** Fetch None ***')

    result = {}
    if _sql.lower().startswith('select') and '*' not in _sql:
        keys = _sql[6:].split('FROM')[0].split('from')[0].strip().split(',')
        result = dict(zip(keys, row))
        logger.info('keys result: %s' % repr(result))

    data = step['data']
    if data:
        for key in data:
            logger.info('key: %s, expect: %s, real: %s' %
                        (repr(key), repr(data[key]), repr(result[key])))
            if data[key].startswith('*'):
                assert data[key][1:] in result[key]
            else:
                assert data[key] == result[key]

    output = step['output']
    if output:
        logger.info('output: %s' % repr(output))
        for key in output:
            g.var[key] = result[output[key]]
