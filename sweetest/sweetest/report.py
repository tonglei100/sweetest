

def reporter(plan_data, testsuite_data, report_data, extra_data):

    extra_data['plan_id'] = plan_data['plan_id']
    extra_data['plan'] = plan_data['plan']    

    testcase = []
    for key, ts in report_data.items():
            count = {'result': 'Pass', 'total': 0, 'pass': 0, 'fail': 0, 'block': 0}
            for tc in ts:
                tc = {**extra_data, **tc}
                
                res = tc['result'].lower()
                if res in count: 
                    count[res] += 1
                    count['total'] += 1
                    testcase.append(tc)
                if count['fail'] + count['block']:
                    count['result'] = 'Fail'
            testsuite_data[key] = {**count, **testsuite_data[key]}

    testsuite = []
    count = {'total': 0, 'pass': 0, 'fail': 0, 'block': 0}
    result = 'Pass'
    for key, ts in testsuite_data.items():
        for k in count:
            count[k] += ts[k]
        if ts['result'] != 'Pass':
            result = 'Fail' 

        ts = {**extra_data, **ts}
        ts['testsuite'] = key
        testsuite.append(ts)
    count['result'] = result

    plan = {**extra_data, **count, **plan_data}

    return plan, testsuite, testcase