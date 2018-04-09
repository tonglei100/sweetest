from copy import deepcopy
from sweetest.globals import g
from sweetest.elements import e
from sweetest.log import logger
from sweetest.parse import data_format
from sweetest.database import DB


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

    logger.info('SQL: %s' % _sql)
    # 获取连接参数
    el, value = e.get(step['page'] + '-' + '配置信息')
    arg = data_format(value)

    if step['page'] not in g.db.keys():
        g.db[step['page']] = DB(arg)
    row = g.db[step['page']].fetchone(_sql)
    logger.info('SQL result: %s' % (row,))

    result = {}
    if _sql.lower().startswith('select') and '*' not in _sql:
        keys = _sql[6:].split('FROM')[0].split('from')[0].strip().split(',')
        result = dict(zip(keys, row))
        logger.info('keys result: %s' % result)

    data = step['data']
    output = step['output']
    if data:
        for key in data:
            logger.info('key: %s, expect: %s, real: %s' %
                        (key, data[key], result[key]))
            if data[key].startswith('*'):
                assert data[key][1:] in result[key]
            else:
                assert data[key] == result[key]

    if output:
        logger.info('output: %s' % output)
        for key in output:
            g.var[key] = result[output[key]]
