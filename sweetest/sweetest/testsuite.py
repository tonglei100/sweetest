import time
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
                testcase['flag'] = 'N'
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
        g.testsuite_data[self.sheet_name] =  self.result


    def setup(self, testcase, case):
        logger.info('Start running the SETUP testcase...')
        # setup 执行成功标记

        def run_setup(testcase):
            if testcase:
                tc = TestCase(testcase)
                tc.run()
                if testcase['result'] == 'Pass':
                    flag = 'Y'
                else:
                    flag = 'N'
            else:
                flag = 'O'
            return flag

        setup_flag = run_setup(self.setup_testcase)

        if setup_flag == 'N':
            base_flag = run_setup(self.base_testcase)
            if base_flag == 'Y':
                setup_flag = run_setup(self.setup_testcase)
                if setup_flag == 'N':
                    testcase['result'] = 'Block'
                    case.block('Blocked', 'SETUP is not Pass')
                    logger.warn('Run the testcase: %s|%s Blocked, SETUP is not Pass' % (
                        testcase['id'], testcase['title']))
                    return False
            elif base_flag == 'O':
                testcase['result'] = 'Block'
                case.block('Blocked', 'SETUP is not Pass')
                logger.warn('Run the testcase: %s|%s Blocked, SETUP is not Pass' % (
                    testcase['id'], testcase['title']))
                return False

        return True

    def run(self):

        self.testsuite_start()

        # 当前测试用例
        current = {'result': 'Pass'}
        # 上一个测试用例
        previous = {}

        # 1.执行用例
        for testcase in self.testsuite:
            # 根据筛选条件，把不需要执行的测试用例跳过
            flag = False
            for k,v in self.conditions.items():
                if not isinstance(v, list):
                    v = [v]
                if testcase[k] not in v:
                    testcase['result'] = '-'
                    flag = True
            if flag:
                continue
            # 统计开始时间
            testcase['start_timestamp'] = timestamp()
            # xml 测试报告-测试用例初始化
            if testcase['flag'] != 'N':
                case = self.report.create_case(
                    testcase['title'], testcase['id'])
                case.start()
                case.priority = testcase['priority']
                # 用例上下文
                previous = current
                current = testcase
            else:
                testcase['result'] = 'Skip'
                # case.skip('Skip', 'Autotest Flag is N')
                logger.info('Run the testcase: %s|%s Skipped, because the flag=N or the condition=snippet' % (
                    testcase['id'], testcase['title']))
                # 统计结束时间
                testcase['end_timestamp'] = timestamp()
                continue

            if testcase['condition'].lower() not in ('base', 'setup'):
                if testcase['condition'].lower() == 'sub':
                    if previous['result'] != 'Pass':
                        testcase['result'] = 'Block'
                        case.block(
                            'Blocked', 'Main or pre Sub testcase is not pass')
                        logger.warn('Run the testcase: %s|%s Blocked, Main or pre Sub TestCase is not Pass' % (
                            testcase['id'], testcase['title']))
                        # 统计结束时间
                        testcase['end_timestamp'] = timestamp()    
                        continue
                # 如果前置条件为 skip，则此用例不执行前置条件
                elif testcase['condition'].lower() == 'skip':
                    pass
                else:
                    result = self.setup(testcase, case)
                    #if result == 'N':
                    if not result:
                        # 统计结束时间
                        testcase['end_timestamp'] = timestamp()
                        continue

            try:
                tc = TestCase(testcase)
                tc.run()

                # 统计结束时间
                testcase['end_timestamp'] = timestamp()

                if testcase['result'] == 'Pass':
                    case.succeed()
                elif testcase['result'] == 'Fail':
                    case.fail('Fail', testcase['report'])
                    if testcase['condition'].lower() == 'base':
                        logger.warn('Run the testcase: %s|%s Fail, BASE is not Pass. Break the AutoTest' % (
                            testcase['id'], testcase['title']))
                        break
                    if testcase['condition'].lower() == 'setup':
                        logger.warn('Run the testcase: %s|%s Fail, SETUP is not Pass. Break the AutoTest' % (
                            testcase['id'], testcase['title']))
                        break
            except Exception as exception:
                case.error('Error', 'Remark:%s |||Exception:%s' %
                           (testcase['remark'], exception))
                logger.exception('Run the testcase: %s|%s fail' %
                                 (testcase['id'], testcase['title']))
                if testcase['condition'].lower() == 'base':
                    logger.warn('Run the testcase: %s|%s Error, BASE is not Pass. Break the AutoTest' % (
                        testcase['id'], testcase['title']))
                    break
                if testcase['condition'].lower() == 'setup':
                    logger.warn('Run the testcase: %s|%s Error, SETUP is not Pass. Break the AutoTest' % (
                        testcase['id'], testcase['title']))
                    break

        self.report.finish()

        # 2.清理环境
        try:
            if g.platform.lower() in ('desktop',):
                w.close()
                g.driver.quit()
                logger.info('--- Quit th Driver: %s' %g.browserName) 
        except:
            logger.exception('Clear the env is fail')

        self.testsuite_end()