from sweetest.exception import Error

class DB:

    def __init__(self, arg):
        self.connect = ''
        self.cursor = ''

        try:
            if arg['type'].lower() == 'mysql':
                import pymysql as mysql
                self.connect = mysql.connect(
                    host=arg['host'], port=arg['port'], user=arg['user'], password=arg['password'], database=arg['dbname'])
                self.cursor = self.connect.cursor()
                sql = 'select version()'

            elif arg['type'].lower() == 'oracle':
                import os
                import cx_Oracle as oracle
                # Oracle查询出的数据，中文输出问题解决
                os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
                self.connect = oracle.connect(arg['user'] + '/' + arg['password'] + '@' + arg['host'] + '/' + arg['sid'])
                self.cursor = self.connect.cursor()
                sql = 'select * from v$version'
            elif arg['type'].lower() == 'sqlserver':
                import pymssql as sqlserver
                self.connect = sqlserver.connect(
                    host=arg['host'], port=arg['port'], user=arg['user'], password=arg['password'], database=arg['dbname'])
                self.cursor = self.connect.cursor()
                sql = 'select @@version'

            self.cursor.execute(sql)
            data = self.cursor.fetchone()

        except Exception as exception:
            print(exception)
            raise Error('%s 连接失败：%s' % (arg['type'], exception))

    def fetchone(self, sql):
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchone()
            return data
        except Exception as exception:
            raise Error('Fetchone fail: %s' % exception)

    def fetchall(self, sql):
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            return data
        except Exception as exception:
            raise Error('Fetchall fail: %s' % exception)

    def execute(self, sql):
        try:
            self.cursor.execute(sql)
            self.connect.commit()
        except Exception as exception:
            raise Error('Execute fail: %s' % exception)

    def __del__(self):
        #self.connect.close()
        pass

if __name__ == '__main__':
    arg = {'type': 'Oracle', 'host': '10.1.50.125', 'port': '3306',\
        'user': 'kims', 'password': '123456', 'dbname': 'test', 'sid':'jzdb'}
    db =DB(arg)
    sql = "select STKPOOLID,STKID,STKNAME,MARKETID,STARTDAY,ENDDAY,ISLOCK,\
        LOCKSTARTDAY,LOCKENDDAY,INVESTTYPE,UPDATER,UPDATETIME,REMARK,CREATER,\
        CREATETIME,SN from ir_stkpool_member_etl where stkpoolid = 'STR_GSYL'"
    result = db.fetchone(sql)
    print(result)
