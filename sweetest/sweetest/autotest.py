
from os import path
import time
import sys
from sweetest.data import testsuite_format, testsuite2data
from sweetest.parse import parse
from sweetest.elements import e
from sweetest.globals import g
from sweetest.windows import w
from sweetest.testsuite import TestSuite
from sweetest.testcase import TestCase
from sweetest.utility import Excel, get_record
from sweetest.log import logging
from sweetest.report import Report
from sweetest.config import _testcase, _elements, _report


class Autotest:
    def __init__(self, file_name, sheet_name, platform='PC', app='Chrome'):
        g.start_time = time.strftime("@%Y%m%d_%H%M%S", time.localtime())

        self.platform = platform
        self.app = app

        g.project_name = file_name.split('-')[0]
        self.testcase_file = path.join('testcase', file_name + '-' + _testcase + '.xlsx')
        self.elements_file = path.join('element', g.project_name + '-' + _elements + '.xlsx')
        self.report_file = path.join('report', file_name + '-' + _report + '.xlsx')
        self.report_xml = path.join('junit', file_name + '-' + _report + '.xml')

        self.testcase_workbook = Excel(self.testcase_file, 'r')
        self.sheet_names = self.testcase_workbook.get_sheet(sheet_name)

        self.report_workbook = Excel(self.report_file.split('.')[
                                     0] + g.start_time + '.xlsx', 'w')


    def plan(self):
        self.code = 0  # 返回码
        # 1.解析配置文件
        try:
            e.get_elements(self.elements_file)
        except Exception as exception:
            logging.critical('Parse config file fail')
            logging.debug(exception)
            self.code = -1
            sys.exit(self.code)

        self.report = Report()
        self.report_ts = {}

        # 2.逐个执行测试套件
        for sheet_name in self.sheet_names:
            g.sheet_name = sheet_name
            # xml 测试报告初始化
            self.report_ts[sheet_name] = self.report.create_suite(g.project_name, sheet_name)
            self.report_ts[sheet_name].start()

            self.run(sheet_name)

        self.report_workbook.close()

        with open(self.report_xml, 'w', encoding='utf-8') as f:
            self.report.write(f)

        sys.exit(self.code)


    def run(self, sheet_name):
        # 1.从 Excel 获取测试用例集
        try:
            data = self.testcase_workbook.read(sheet_name)
            testsuite = testsuite_format(data)
            logging.debug('Testsuite imported from Excle:\n' + str(testsuite))
            logging.info('From Excel import testsuite success')
        except Exception as exception:
            logging.critical('From Excel import testsuite fail')
            logging.debug(exception)
            self.code = -1
            sys.exit(self.code)

        # 2.初始化全局对象
        try:
            g.set_driver(self.platform, self.app)
            # 如果测试数据文件存在，则从该文件里读取一行数据，赋值到全局变量列表里
            data_file = path.join('data', g.project_name + '-' + sheet_name + '.csv')
            if path.exists(data_file):
                g.var = get_record(data_file)
            w.init()
        except Exception as exception:
            logging.critical('Init global object fail')
            logging.debug(exception)
            self.code = -1
            sys.exit(self.code)

        # 3.解析测试用例集
        try:
            parse(testsuite)
            logging.debug('testsuite has been parsed:\n' + str(testsuite))
        except Exception as exception:
            logging.critical('Parse testsuite fail')
            logging.debug(exception)
            self.code = -1
            sys.exit(self.code)


        # 4.执行测试套件
        ts = TestSuite(testsuite, self.report_ts[sheet_name])
        ts.run()

        # 5.判断测试结果
        if self.report_ts[sheet_name].high_errors + self.report_ts[sheet_name].medium_errors + \
        self.report_ts[sheet_name].high_failures + self.report_ts[sheet_name].medium_failures:
            self.code = -1

        # 6.保存测试结果
        try:
            data = testsuite2data(testsuite)
            self.report_workbook.write(data, sheet_name)
        except Exception as exception:
            logging.warn('Save the report is fail')
            logging.debug(exception)
