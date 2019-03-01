

def reporter(plan_data, testsuite_data, report_data, extra_data):

    extra_data['plan'] = plan_data['plan']    
    extra_data['task'] = plan_data['task']

    testcase = []
    for key, ts in report_data.items():
            count = {'result': 'success', 'total': 0,
                     'success': 0, 'failure': 0, 'blocked': 0}
            no = 1
            for tc in ts:
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
