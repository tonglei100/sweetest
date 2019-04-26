import time


def reporter(plan_data, testsuites_data, report_data, extra_data):

    extra_data['plan'] = plan_data['plan']
    extra_data['task'] = int(time.time() * 1000)

    testcases = []
    for key, ts in report_data.items():
        count = {'result': 'success', 'total': 0,
                 'success': 0, 'failure': 0, 'blocked': 0}
        no = 1
        for tc in ts:
            tc['testsuite'] = key
            tc['no'] = no
            no += 1
            tc = {**extra_data, **tc}

            res = tc['result'].lower()
            if tc['condition'].lower() in ('base', 'setup', 'snippet'):
                pass
            elif res in count:
                count[res] += 1
                count['total'] += 1
            testcases.append(tc)
            if count['failure'] + count['blocked']:
                count['result'] = 'failure'
        testsuites_data[key] = {**count, **testsuites_data[key]}

    testsuite = []
    count = {'total': 0, 'success': 0,
             'failure': 0, 'blocked': 0}
    result = 'success'
    for key, ts in testsuites_data.items():
        for k in count:
            count[k] += ts[k]
        if ts['result'] != 'success':
            result = 'failure'

        ts = {**extra_data, **ts}
        ts['testsuite'] = key
        testsuite.append(ts)
    count['result'] = result

    plan = {**extra_data, **count, **plan_data}

    return plan, testsuite, testcases


def local_time(timestamp):
    import time
    t = time.localtime(int(timestamp / 1000))
    return str(time.strftime("%Y/%m/%d %H:%M:%S", t))


def cost_time(start, end):
    return int((end - start) / 1000)


def summary(plan_data, testsuites_data, report_data, extra_data):
    plan, testsuites, testcases = reporter(
        plan_data, testsuites_data, report_data, extra_data)

    data = [['测试套件', '用例总数', '成功', '阻塞', '失败', '测试结果', '开始时间', '结束时间', '耗时(秒)']]
    failures = [['测试套件', '用例编号', '用例标题', '用例结果', '失败步骤', '备注']]

    for suite in testsuites:
        row = [suite['testsuite'], suite['total'], suite['success'], suite['blocked'], suite['failure'],
               suite['result'], local_time(suite['start_timestamp']), local_time(suite['end_timestamp']),
               cost_time(suite['start_timestamp'], suite['end_timestamp'])]
        data.append(row)

    flag = False
    for case in testcases:
        suite_name = '' if flag else case['testsuite']
        row = []
        if case['result'] == 'blocked':
            row = [suite_name, case['id'], case['title'], case['result']]
        elif case['result'] == 'failure':
            for step in case['steps']:
                if step['score'] == 'NO':
                    desc = '|'.join([step[k] for k in ('no', 'keyword', 'page', 'element')])
                    row = [suite_name, case['id'], case['title'], case['result'], desc, step['remark']]
                    break
        if row:
            flag = True
            failures.append(row)

    data.append(['--------'])
    total = ['总计', plan['total'], plan['success'], plan['blocked'], plan['failure'],
             plan['result'], local_time(plan['start_timestamp']), local_time(plan['end_timestamp']),
             cost_time(plan['start_timestamp'], plan['end_timestamp'])]

    data.append(total)
    if len(failures) > 1:
        data.append(['********'])
        data += failures
    return data
