from injson import check
from sweet import log, vars
from sweet.utility import compare, json2dict


keywords = {
    'SQL': 'SQL'
}


class App:

    keywords = keywords

    def __init__(self, setting):
        # 获取连接参数
        self.db = DB(setting)

    def _close(self):
        pass

    def _call(self, step):
        # 根据关键字调用关键字实现
        getattr(self, step['keyword'].lower())(step)

    def sql(self, step):

        response = {}

        _sql = step['element']

        log.debug(f'SQL: {repr(_sql)}')

        row = {}
        if _sql.lower().startswith('select'):
            row = self.db.fetchone(_sql)
            log.debug(f'SQL response: {repr(row)}')
            if not row:
                raise Exception('*** Fetch None ***')

        elif _sql.lower().startswith('db.'):
            _sql_ = _sql.split('.', 2)
            collection = _sql_[1]
            sql = _sql_[2]
            response = self.db.mongo(collection, sql)
            if response:
                log.debug(f'find result: {repr(response)}')
        else:
            self.db.execute(_sql)

        if _sql.lower().startswith('select'):
            text = _sql[6:].split('FROM')[0].split('from')[0].strip()
            keys = dedup(text).split(',')
            for i, k in enumerate(keys):
                keys[i] = k.split(' ')[-1]
            response = dict(zip(keys, row))
            log.debug(f'select result: {repr(response)}')

        expected = step['data']
        if not expected:
            expected = step['expected']
        if 'json' in expected:
            expected['json'] = json2dict(expected.get('json', '{}'))
            result = check(expected.pop('json'), response['json'])
            log.debug(f'json check result: {result}')
            if result['code'] != 0:
                raise Exception(
                    f'json | EXPECTED:{repr(expected["json"])}, REAL:{repr(response["json"])}, RESULT: {result}')
            elif result['var']:
                vars.put(result['var'])
                log.debug(f'json var: {repr(result["var"])}')

        if expected:
            for key in expected:
                sv, pv = expected[key], response[key]
                log.debug(f'key: {repr(key)}, expect: {repr(sv)}, real: { repr(pv)}')

                compare(sv, pv)

        output = step['output']       
        if output:

            for k, v in output.items():
                if k == 'json':
                    sub = json2dict(output.get('json', '{}'))
                    result = check(sub, response['json'])
                    vars.put(result['var'])
                    log.debug(f'json var: {repr(result["var"])}')
                else:
                    vars.put({k: response[v]})
            log.debug(f'output: {vars.output()}')


def dedup(text):
    '''
    去掉 text 中括号及其包含的字符
    '''
    _text = ''
    n = 0

    for s in text:
        if s not in ('(', ')'):
            if n <= 0:
                _text += s
        elif s == '(':
            n += 1
        elif s == ')':
            n -= 1
    return _text


class DB:

    def __init__(self, arg):
        self.connect = ''
        self.cursor = ''
        self.db = ''

        try:
            if arg['type'].lower() == 'mongodb':
                import pymongo
                host = arg.pop('host') if arg.get(
                    'host') else 'localhost:27017'
                host = host.split(',') if ',' in host else host
                port = int(arg.pop('port')) if arg.get('port') else 27017
                if arg.get('user'):
                    arg['username'] = arg.pop('user')
                # username = arg['user'] if arg.get('user') else ''
                # password = arg['password'] if arg.get('password') else ''
                # self.connect = pymongo.MongoClient('mongodb://' + username + password + arg['host'] + ':' + arg['port'] + '/')
                self.connect = pymongo.MongoClient(host=host, port=port, **arg)
                self.connect.server_info()
                self.db = self.connect[arg['dbname']]

                return

            sql = ''
            if arg['type'].lower() == 'mysql':
                import pymysql as mysql
                self.connect = mysql.connect(
                    host=arg['host'], port=int(arg['port']), user=arg['user'], password=arg['password'], database=arg['dbname'], charset=arg.get('charset', 'utf8'))
                self.cursor = self.connect.cursor()
                sql = 'select version()'

            elif arg['type'].lower() == 'oracle':
                import os
                import cx_Oracle as oracle
                # Oracle查询出的数据，中文输出问题解决
                os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
                self.connect = oracle.connect(
                    arg['user'] + '/' + arg['password'] + '@' + arg['host'] + '/' + arg['sid'])
                self.cursor = self.connect.cursor()
                sql = 'select * from v$version'
            elif arg['type'].lower() == 'sqlserver':
                import pymssql as sqlserver
                self.connect = sqlserver.connect(
                    host=arg['host'], port=arg['port'], user=arg['user'], password=arg['password'], database=arg['dbname'], charset=arg.get('charset', 'utf8'))
                self.cursor = self.connect.cursor()
                sql = 'select @@version'

            self.cursor.execute(sql)
            self.cursor.fetchone()

        except:
            log.exception(f'*** {arg["type"]} connect is failure ***')
            raise

    def fetchone(self, sql):
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchone()
            self.connect.commit()
            return data
        except:
            log.exception('*** fetchone failure ***')
            raise

    def fetchall(self, sql):
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            self.connect.commit()
            return data
        except:
            log.exception('*** Fetchall failure ***')
            raise

    def execute(self, sql):
        try:
            self.cursor.execute(sql)
            self.connect.commit()
        except:
            log.exception('*** execute failure ***')
            raise

    def mongo(self, collection, sql):
        try:
            cmd = 'self.db[\'' + collection + '\'].' + sql
            result = eval(cmd)
            if sql.startswith('find_one'):
                return result
            elif sql.startswith('find'):
                for d in result:
                    return d
            elif 'count' in sql:
                return {'count': result}
            else:
                return {}
        except:
            log.exception('*** execute failure ***')
            raise

    def __del__(self):
        self.connect.close()
