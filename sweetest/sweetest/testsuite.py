from sweetest.globals import g
from sweetest.windows import w
from sweetest.testcase import TestCase
from sweetest.log import logger


class TestSuite:
    def __init__(self, testsuite, report):
        self.testsuite = testsuite
        self.report = report

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

    def setup(self):
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

        # 当前测试用例
        current = {'result': 'Pass'}
        # 上一个测试用例
        previous = {}

        # 1.执行用例
        for testcase in self.testsuite:
            previous = current
            current = testcase

            # xml 测试报告-测试用例初始化
            if testcase['flag'] != 'N':
                case = self.report.create_case(
                    testcase['title'], testcase['id'])
                case.start()
                case.priority = testcase['priority']
            else:
                testcase['result'] = 'Skip'
                # case.skip('Skip', 'Autotest Flag is N')
                logger.warn('Run the testcase: %s|%s Skipped, because the flag=N or the condition=snippet' % (
                    testcase['id'], testcase['title']))
                continue

            if testcase['condition'].lower() not in ('base', 'setup'):
                if testcase['condition'].lower() == 'sub':
                    if previous['result'] != 'Pass':
                        testcase['result'] = 'Block'
                        case.block(
                            'Blocked', 'Main or pre Sub testcase is not pass')
                        logger.warn('Run the testcase: %s|%s Blocked, Main or pre Sub TestCase is not Pass' % (
                            testcase['id'], testcase['title']))
                        continue
                else:
                    result = self.setup()
                    if result == 'N':
                        continue

            try:
                tc = TestCase(testcase)
                tc.run()
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
            for handle in w.windows.values():
                g.driver.switch_to_window(handle)
                g.driver.close()
        except:
            logger.exception('Clear the env is fail')
