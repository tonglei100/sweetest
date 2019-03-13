import time


def reporter(plan_data, testsuite_data, report_data, extra_data):

    extra_data['plan'] = plan_data['plan']
    extra_data['task'] = int(time.time() * 1000)

    testcase = []
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
            testcase.append(tc)
            if count['failure'] + count['blocked']:
                count['result'] = 'failure'
        testsuite_data[key] = {**count, **testsuite_data[key]}

    testsuite = []
    count = {'total': 0, 'success': 0,
             'failure': 0, 'blocked': 0}
    result = 'success'
    for key, ts in testsuite_data.items():
        for k in count:
            count[k] += ts[k]
        if ts['result'] != 'success':
            result = 'failure'

        ts = {**extra_data, **ts}
        ts['testsuite'] = key
        testsuite.append(ts)
    count['result'] = result

    plan = {**extra_data, **count, **plan_data}

    return plan, testsuite, testcase


def local_time(timestamp):
    import time
    t = time.localtime(int(timestamp / 1000))
    return str(time.strftime("%Y/%m/%d %H:%M:%S", t))


def cost_time(start, end):
    return int((end - start) / 1000)


def summary(plan_data, testsuite_data, report_data, extra_data):
    plan, testsuite = reporter(
        plan_data, testsuite_data, report_data, extra_data)[:2]

    data = [['测试套件', '用例总数', '成功', '阻塞', '失败', '测试结果', '开始时间', '结束时间', '耗时(秒)']]
 
    for s in testsuite:
        row = [s['testsuite'], s['total'], s['success'], s['blocked'], s['failure'],
               s['result'], local_time(s['start_timestamp']), local_time(s['end_timestamp']),
               cost_time(s['start_timestamp'], s['end_timestamp'])]
        data.append(row)

    data.append(['--------'])
    total = ['总计', plan['total'], plan['success'], plan['blocked'], plan['failure'],
             plan['result'], local_time(plan['start_timestamp']), local_time(plan['end_timestamp']),
             cost_time(plan['start_timestamp'], plan['end_timestamp'])]
    data.append(total)
    return data
