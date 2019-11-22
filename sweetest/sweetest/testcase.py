from time import sleep
from pathlib import Path
import re
from sweetest.log import logger
from sweetest.globals import g, now, timestamp
from sweetest.elements import e
from sweetest.windows import w
from sweetest.snapshot import Snapshot
from sweetest.locator import locating_elements, locating_data, locating_element
from sweetest.keywords import web, common, mobile, http, files
from sweetest.config import web_keywords, common_keywords, mobile_keywords, http_keywords, windows_keywords, files_keywords
from sweetest.utility import replace_dict, replace


def elements_format(page, element):
    if not page:
        page = g.current_page

    if not element:
        return page, '', element

    if page in ('SNIPPET', '用例片段') or element in ('变量赋值',):
        return page, '', element

    elements = element.split('|')
    if len(elements) == 1:
        custom, el = e.have(page, element)
        g.current_page = page
        return page, custom, el
    else:
        els = []
        for _element in elements:
            custom, el = e.have(page, _element.strip())
            els.append(el)
        g.current_page = page
        return page, custom, els


def v_data(d, _d):
    data = ''
    if ',,' in str(_d):
        s = ',,'
    else:
        s = ','

    for k, v in d.items():
        data += k + '=' + str(v) + s

    if s ==',,':
        return data[:-2]
    else:
        return data[:-1]


def test_v_data():
    data = {'a': 1, 'b': 'b'}
    _data = "{'a': 1,, 'b': 'b'}"
    return v_data(data, _data)


class TestCase:
    def __init__(self, testcase):
        self.testcase = testcase
        self.snippet_steps = {}

    def run(self):         
        logger.info('>>> Run the TestCase: %s|%s' %
                    (self.testcase['id'], self.testcase['title']))
        self.testcase['result'] = 'success'
        self.testcase['report'] = ''
        if_result = ''

        for index, step in enumerate(self.testcase['steps']):
            # 统计开始时间
            step['start_timestamp'] = timestamp()
            step['snapshot'] = {}

            # if 为否，不执行 then 语句
            if step['control'] == '>' and not if_result:
                step['score'] = '-'
                step['end_timestamp'] = timestamp()
                logger.info('Skipped the <then> Step: %s|%s|%s|%s' %(step['no'], step['page'], step['keyword'], step['element']))
                continue

            # if 为真，不执行 else 语句
            if step['control'] == '<' and if_result:
                step['score'] = '-'
                step['end_timestamp'] = timestamp()
                logger.info('Skipped the <else> Step: %s|%s|%s|%s' %(step['no'], step['page'], step['keyword'], step['element']))
                continue

            if not (g.platform.lower() in ('windows',) and step['keyword'].upper() in windows_keywords):
                step['page'], step['custom'], step['element'] = elements_format(
                    step['page'], step['element'])
            label = g.sheet_name + '#' + \
                self.testcase['id'] + '#' + str(step['no']).replace('<', '(').replace('>', ')').replace('*', 'x')

            logger.info('Run the Step: %s|%s|%s|%s' %
                        (step['no'], step['page'], step['keyword'], step['element']))

            snap = Snapshot()
            try:
                after_function = step['data'].pop('AFTER_FUNCTION', '')

                # 处理强制等待时间
                t = step['data'].pop('等待时间', 0)
                sleep(float(t))

                if isinstance(step['element'], str):
                    step['element'] = replace(step['element'])
                    step['_element'] = step['element']
                elif isinstance(step['element'], list):
                    for i in range(len(step['element'])):
                        step['element'][i] = replace(step['element'][i])
                    step['_element'] = '|'.join(step['element'])

                # 变量替换
                replace_dict(step['data'])
                replace_dict(step['expected'])

                step['data'].pop('BEFORE_FUNCTION', '')

                step['vdata'] = v_data(step['data'], step['_data'])

                if g.platform.lower() in ('desktop',) and step['keyword'].upper() in web_keywords:
                    # 处理截图数据
                    snap.pre(step, label)

                    if step['keyword'].upper() not in ('MESSAGE', '对话框'):
                        # 判断页面是否已和窗口做了关联，如果没有，就关联当前窗口，如果已关联，则判断是否需要切换
                        w.switch_window(step['page'])
                        # 切换 frame 处理，支持变量替换
                        frame = replace(step['custom'])
                        w.switch_frame(frame)

                    # 根据关键字调用关键字实现
                    element = getattr(web, step['keyword'].lower())(step)
                    snap.web_shot(step, element)

                elif g.platform.lower() in ('ios', 'android') and step['keyword'].upper() in mobile_keywords:
                    # 切換 context 處理
                    context = replace(step['custom']).strip()
                    w.switch_context(context)

                    if w.current_context.startswith('WEBVIEW'):
                        # 切换标签页
                        tab = step['data'].get('标签页')
                        if tab:
                            del step['data']['标签页']
                            g.driver.switch_to_window(w.windows[tab])
                        logger.info('Current Context: %s' %
                                    repr(w.current_context))

                    # 根据关键字调用关键字实现
                    getattr(mobile, step['keyword'].lower())(step)

                elif g.platform.lower() in ('windows',) and step['keyword'].upper() in windows_keywords:
                    from sweetest.keywords import windows
                    _page = ''
                    if step['page'].startswith('#'):
                        _page = step['page'][1:]
                        page = [x for x in re.split(r'(<|>)', _page) if x !='']
                    else:
                        page = [x for x in re.split(r'(<|>)', step['page']) if x !='']

                    if _page:
                        dialog = g.windows['#'].dialog(page)
                    else:    
                        dialog = g.windows['default'].dialog(page)
                    #dialog.wait('ready')

                    snap.pre(step, label)

                    # 根据关键字调用关键字实现
                    getattr(windows, step['keyword'].lower())(dialog, step)
                    snap.windows_shot(dialog, step)

                elif step['keyword'].upper() in http_keywords:
                    # 根据关键字调用关键字实现
                    getattr(http, step['keyword'].lower())(step)

                elif step['keyword'].upper() in files_keywords:
                    # 根据关键字调用关键字实现
                    getattr(files, step['keyword'].lower())(step)

                elif step['keyword'].lower() == 'execute':                  
                    result, steps = getattr(
                        common, step['keyword'].lower())(step)
                    self.testcase['result'] = result
                    if step['page'] in ('SNIPPET', '用例片段'):
                        self.snippet_steps[index + 1] = steps
                    if result != 'success':
                        step['end_timestamp'] = timestamp()
                        break

                    # elif step['page'] in ('SCRIPT', '脚本'):
                    #     # 判断页面是否已和窗口做了关联，如果没有，就关联当前窗口，如果已关联，则判断是否需要切换
                    #     w.switch_window(step['page'])
                    #     # 切换 frame 处理，支持变量替换
                    #     frame = replace(step['custom'])
                    #     w.switch_frame(frame)
                    #     common.script(step)

                else:
                    # 根据关键字调用关键字实现
                    getattr(common, step['keyword'].lower())(step)
                logger.info('--- success ---')
                step['score'] = 'OK'

                # if 语句结果赋值
                if step['control'] == '^':
                    if_result = True

                if after_function:
                    replace_dict({'after_function': after_function})
                # 操作后，等待0.2秒
                sleep(0.2)
            except Exception as exception:

                if g.platform.lower() in ('desktop',) and step['keyword'].upper() in web_keywords:
                    file_name = label + now() + '#Failure' +'.png'
                    step['snapshot']['Failure'] = str(snap.snapshot_folder / file_name)                    
                    try:
                        if w.frame != 0:
                            g.driver.switch_to.default_content()
                            w.frame = 0
                        g.driver.get_screenshot_as_file(step['snapshot']['Failure'])
                    except:
                        logger.exception(
                            '*** save the screenshot is failure ***')

                elif g.platform.lower() in ('ios', 'android') and step['keyword'].upper() in mobile_keywords:
                    file_name = label + now() + '#Failure' +'.png'
                    step['snapshot']['Failure'] = str(snap.snapshot_folder / file_name)                      
                    try:
                        g.driver.switch_to.context('NATIVE_APP')
                        w.current_context = 'NATIVE_APP'
                        g.driver.get_screenshot_as_file(u'%s' %step['snapshot']['Failure'])
                    except:
                        logger.exception('*** save the screenshot is failure ***')

                logger.exception('+++ failure +++')
                step['score'] = 'NO'

                step['remark'] += str(exception)
                step['end_timestamp'] = timestamp()

                # if 语句结果赋值
                if step['control'] == '^':
                    if_result = False
                    continue

                self.testcase['result'] = 'failure'
                self.testcase['report'] = 'step-%s|%s|%s: %s' % (
                    step['no'], step['keyword'], step['element'], exception)
                break

            # 统计结束时间
            step['end_timestamp'] = timestamp()

        steps = []
        i = 0
        for k in self.snippet_steps:
            steps += self.testcase['steps'][i:k] + self.snippet_steps[k]
            i = k
        steps += self.testcase['steps'][i:]
        self.testcase['steps'] = steps
