from sweetest.log import logger


class DB:

    def __init__(self, arg):
        self.connect = ''
        self.cursor = ''

        try:
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
            data = self.cursor.fetchone()

        except:
            logger.exception('*** %s connect is fail ***' % arg['type'])
            raise

    def fetchone(self, sql):
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchone()
            self.connect.commit()
            return data
        except:
            logger.exception('*** Fetchone fail ***')
            raise

    def fetchall(self, sql):
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            self.connect.commit()
            return data
        except:
            logger.exception('*** Fetchall fail ***')
            raise

    def execute(self, sql):
        try:
            self.cursor.execute(sql)
            self.connect.commit()
        except:
            logger.exception('*** Execute fail ***')
            raise

    def __del__(self):
        self.connect.close()


if __name__ == '__main__':
    arg = {'type': 'Oracle', 'host': '10.1.50.125', 'port': '3306',
           'user': 'kims', 'password': '123456', 'dbname': 'test', 'sid': 'jzdb'}
    db = DB(arg)
    sql = "select STKPOOLID,STKID,STKNAME,MARKETID,STARTDAY,ENDDAY,ISLOCK,\
        LOCKSTARTDAY,LOCKENDDAY,INVESTTYPE,UPDATER,UPDATETIME,REMARK,CREATER,\
        CREATETIME,SN from ir_stkpool_member_etl where stkpoolid = 'STR_GSYL'"
    result = db.fetchone(sql)
    print(result)
