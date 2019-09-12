import time
from copy import deepcopy
from sweetest.globals import g, timestamp
from sweetest.windows import w
from sweetest.testcase import TestCase
from sweetest.log import logger


class TestSuite:
    def __init__(self, testsuite, sheet_name, report, conditions={}):
        self.testsuite = testsuite
        self.sheet_name = sheet_name
        self.report = report
        self.conditions = conditions
        self.result = {}

        # base 在整个测试套件中首先执行一次
        self.base_testcase = {}
        # setup 在每个测试用例执行之前执行一次
        self.setup_testcase = {}
        for testcase in self.testsuite:
            if testcase['condition'].lower() == 'base':
                self.base_testcase = testcase
            elif testcase['condition'].lower() == 'setup':
                self.setup_testcase = testcase
                testcase['flag'] = 'N'  # setup 用例只在执行其他普通用例之前执行
            elif testcase['condition'].lower() == 'snippet':
                g.snippet[testcase['id']] = testcase
                testcase['flag'] = 'N'

    def testsuite_start(self):
        self.result['no'] = g.no
        g.no += 1
        self.result['testsuite'] = self.sheet_name
        self.result['start_timestamp'] = timestamp()

    def testsuite_end(self):
        self.result['end_timestamp'] = timestamp()
        g.testsuite_data[self.sheet_name] = self.result

    def setup(self, testcase, case):
        logger.info('='*50)         
        if self.setup_testcase:
            logger.info('*** SETUP testcase ***')
        else:
            logger.info('...No SETUP testcase need to run...')

        def run_setup(testcase):
            if testcase:
                tc = TestCase(testcase)
                tc.run()
                if testcase['result'] == 'success':
                    flag = 'Y'
                else:
                    flag = 'N'
            else:
                flag = 'O'
            return flag
        setup_flag = run_setup(deepcopy(self.setup_testcase))

        if setup_flag == 'N':
            base_flag = run_setup(deepcopy(self.base_testcase))
            if base_flag == 'Y':
                setup_flag = run_setup(deepcopy(self.setup_testcase))
                if setup_flag == 'N':
                    testcase['result'] = 'blocked'
                    case.block('Blocked', 'SETUP is not success')
                    logger.warn('Run the testcase: %s|%s blocked, SETUP is not success' % (
                        testcase['id'], testcase['title']))
                    return False
            elif base_flag == 'O':
                testcase['result'] = 'blocked'
                case.block('Blocked', 'SETUP is not success')
                logger.warn('Run the testcase: %s|%s blocked, SETUP is not success' % (
                    testcase['id'], testcase['title']))
                return False

        return True

    def run(self):

        self.testsuite_start()

        # 当前测试用例
        current = {'result': 'success'}
        # 上一个测试用例
        previous = {}

        # 前置条件执行失败标志，即未执行用例阻塞标志
        blcoked_flag = False

        # 1.执行用例
        for testcase in self.testsuite:
            # 根据筛选条件，把不需要执行的测试用例跳过
            flag = False
            for k, v in self.conditions.items():
                if not isinstance(v, list):
                    v = [v]
                if testcase[k] not in v:
                    testcase['result'] = 'skipped'
                    flag = True
            if flag:
                continue

            # 统计开始时间
            testcase['start_timestamp'] = timestamp()
            # xml 测试报告-测试用例初始化
            if testcase['flag'] != 'N':
                # 如果前置条件失败了，直接设置为阻塞
                if blcoked_flag:
                    testcase['result'] = 'blocked'
                    testcase['end_timestamp'] = timestamp()
                    continue

                case = self.report.create_case(
                    testcase['title'], testcase['id'])
                case.start()
                case.priority = testcase['priority']
                # 用例上下文
                previous = current
                
                current = testcase
            else:
                testcase['result'] = 'skipped'
                # case.skip('Skip', 'Autotest Flag is N')
                # logger.info('Run the testcase: %s|%s skipped, because the flag=N or the condition=snippet' % (
                #     testcase['id'], testcase['title']))
                # 统计结束时间
                testcase['end_timestamp'] = timestamp()
                continue

            if testcase['condition'].lower() not in ('base', 'setup'):
                if testcase['condition'].lower() == 'sub':
                    if previous['result'] != 'success':
                        testcase['result'] = 'blocked'
                        case.block(
                            'Blocked', 'Main or pre Sub testcase is not success')
                        logger.warn('Run the testcase: %s|%s blocked, Main or pre Sub TestCase is not success' % (
                            testcase['id'], testcase['title']))
                        # 统计结束时间
                        testcase['end_timestamp'] = timestamp()
                        continue
                # 如果前置条件为 skip，则此用例不执行前置条件
                elif testcase['condition'].lower() == 'skip':
                    pass
                else:
                    result = self.setup(testcase, case)
                    # if result == 'N':
                    if not result:
                        # 统计结束时间
                        testcase['end_timestamp'] = timestamp()
                        continue

            try:
                tc = TestCase(testcase)
                logger.info('-'*50)
                tc.run()

                # 统计结束时间
                testcase['end_timestamp'] = timestamp()

                if testcase['result'] == 'success':
                    case.succeed()
                elif testcase['result'] == 'failure':
                    case.fail('Failure', testcase['report'])
                    if testcase['condition'].lower() == 'base':
                        logger.warn('Run the testcase: %s|%s Failure, BASE is not success. Break the AutoTest' % (
                            testcase['id'], testcase['title']))
                        blcoked_flag = True
                        continue
                    if testcase['condition'].lower() == 'setup':
                        logger.warn('Run the testcase: %s|%s failure, SETUP is not success. Break the AutoTest' % (
                            testcase['id'], testcase['title']))
                        blcoked_flag = True
                        continue
            except Exception as exception:
                case.error('Error', 'Remark:%s |||Exception:%s' %
                           (testcase['remark'], exception))
                logger.exception('Run the testcase: %s|%s failure' %
                                 (testcase['id'], testcase['title']))
                if testcase['condition'].lower() == 'base':
                    logger.warn('Run the testcase: %s|%s error, BASE is not success. Break the AutoTest' % (
                        testcase['id'], testcase['title']))
                    blcoked_flag = True
                    continue
                if testcase['condition'].lower() == 'setup':
                    logger.warn('Run the testcase: %s|%s error, SETUP is not success. Break the AutoTest' % (
                        testcase['id'], testcase['title']))
                    blcoked_flag = True
                    continue

        self.report.finish()

        # 2.清理环境
        try:
            if g.platform.lower() in ('desktop',):
                # w.close()
                g.driver.quit()
                logger.info('--- Quit th Driver: %s' % g.browserName)
        except:
            logger.exception('Clear the env is fail')

        self.testsuite_end()
