from sweetest.log import logger


class DB:

    def __init__(self, arg):
        self.connect = ''
        self.cursor = ''
        self.db = ''

        try:
            if arg['type'].lower() == 'mongodb':
                import pymongo
                host = arg.pop('host') if arg.get('host') else 'localhost:27017'
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
            logger.exception('*** %s connect is failure ***' % arg['type'])
            raise

    def fetchone(self, sql):
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchone()
            self.connect.commit()
            return data
        except:
            logger.exception('*** Fetchone failure ***')
            raise

    def fetchall(self, sql):
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            self.connect.commit()
            return data
        except:
            logger.exception('*** Fetchall failure ***')
            raise

    def execute(self, sql):
        try:
            self.cursor.execute(sql)
            self.connect.commit()
        except:
            logger.exception('*** Execute failure ***')
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
            logger.exception('*** Execute failure ***')
            raise            

    def __del__(self):
        self.connect.close()
