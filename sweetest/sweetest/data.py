import xlrd
from sweetest.utility import Excel, data2dict
from sweetest.config import header


def testsuite_format(data):
    '''
    将元素为 dict 的 list，处理为 testcase 的 list
    testcase 的格式：
    {
        'id': 'Login_001',  #用例编号
        'title': 'Login OK',  #用例标题
        'condition': '',  #前置条件
        'designer': 'Leo',  #设计者
        'flag': '',  #自动化标记
        'result': '',  #测试结果
        'remark': '',  #备注
        'steps':
            [
                {
                'no': 1,  #步骤编号
                'action': '输入',
                'page': '产品管系统登录页',
                'elements': '用户名'
                'data': 'user1',  #测试数据
                'output': '',  #输出数据
                'result': '',  #测试结果
                'remark': ''  #备注
                },
                {……}
                ……
            ]
    }
    '''
    testsuite = []
    testcase = {}
    data = data2dict(data)

    for d in data:
        # 如果用例编号不为空，则为新的用例
        if d['用例编号'].strip():
            # 如果 testcase 非空，则添加到 testcases 里，并重新初始化 testcase
            if testcase:
                testsuite.append(testcase)
                testcase = {}
            testcase['id'] = d['用例编号']
            testcase['title'] = d['用例标题']
            testcase['condition'] = d['前置条件']
            if d['优先级']:
                testcase['priority'] = d['优先级']
            else:
                testcase['priority'] = 'M'
            testcase['designer'] = d['设计者']
            testcase['flag'] = d['自动化标记']
            testcase['result'] = d['测试结果']
            testcase['remark'] = d['备注']
            testcase['steps'] = []
        # 如果步骤编号不为空，则为有效步骤，否则用例解析结束
        no = str(d['步骤编号']).strip()
        if no:
            step = {}
            step['control'] = ''
            if no[0] in ('^', '>', '<', '#'):
                step['control'] = no[0]
                step['no'] = no
            else:
                step['no'] = int(d['步骤编号'])
            step['action'] = d['操作']
            step['page'] = d['页面']
            step['elements'] = d['元素']
            step['data'] = d['测试数据']
            step['output'] = d['输出数据']
            step['result'] = d['测试结果']
            step['remark'] = d['备注']
            # 仅作为测试结果输出时，保持原样
            step['元素'] = d['元素']
            step['测试数据'] = d['测试数据']
            step['输出数据'] = d['输出数据']
            testcase['steps'].append(step)
    if testcase:
        testsuite.append(testcase)
    return testsuite


def testsuite_from_excel(file_name, sheet_name):
    d = Excel(file_name)
    return testsuite_format(data2dict(d.read(sheet_name)))


def testsuite2data(data):
    list_list_data = [header]
    for d in data:
        testcase = [d['id'], d['title'], d['condition'], '', '', '', '',
                    '', '', d['priority'], d['designer'], d['flag'], d['result'], d['remark']]
        list_list_data.append(testcase)
        for s in d['steps']:
            step = ['', '', '', s['no'], s['action'], s['page'], s['元素'],
                    s['测试数据'], s['输出数据'], '', '', '', s['result'], s['remark']]
            list_list_data.append(step)
    return list_list_data
