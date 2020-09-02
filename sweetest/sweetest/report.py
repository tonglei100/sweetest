import time
import arrow
from pathlib import Path
from sweetest.globals import g
from sweetest.utility import mkdir


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

def markdown(plan, testsuites, testcases, md_path='markdown'):
    success = OK = '<font color=#00BB00>通过</font>'
    failure = NO = '<font color=#FF0000>失败</font>'
    blocked = '<font color=#FFD306>阻塞</font>'
    skipped = '<font color=#6C6C6C>-</font>'

    md = '| 测试套件名称 | 开始时间 | 结束时间 | 耗时 | 成功个数 | 失败个数 | 阻塞个数 | 总个数 | 结果 |\n'
    md +='| ----------- | ------- | ------- | ---- | ------- | ------- | -------- | ----- | ---- |\n'

    result = success
    sc, fc, bc, tc = 0, 0, 0, 0
    for v in testsuites.values():
        sc += v['success']
        fc += v['failure'] 
        bc += v['blocked']
        tc += v['total']
        re = success
        if v['result'] == 'failure':
            re = failure
        cost = round((v['end_timestamp'] - v['start_timestamp'])/1000, 1)  
        md += f'| {v["testsuite"]} | {tm(v["start_timestamp"])} | {tm(v["end_timestamp"])} | {cost} | '
        md += f'{v["success"]} | {v["failure"]} | {v["blocked"]} | {v["total"]} | {re} |\n'
        if v['result'] == 'failure':
            result = failure
    cost = round((plan['end_timestamp'] - plan['start_timestamp'])/1000, 1)
    md += f'| **共计** | {tm(plan["start_timestamp"])} | {tm(plan["end_timestamp"])}  | {cost} | '
    md += f'{sc} | {fc} | {bc} | {tc} | {result} |\n'
    title = f'# 「{plan["plan"]}」自动化测试执行报告 {result} #\n\n[历史记录](/{plan["plan"]}/)\n\n'
    md = title + f'## 测试计划执行结果\n\n{md}\n\n## 测试套件执行结果\n\n'

    if result == success:
        icon = '✔️'
    else:
        icon = '❌'

    message = f'- {icon} <font color=#9D9D9D size=2>{tm(plan["start_timestamp"])} - {tm(plan["end_timestamp"])}</font> 测试计划'
    message +=f'「[{plan["plan"]}]({plan["plan"]}/{plan["plan"]}_{tm(plan["start_timestamp"], "_")})」执行完成，测试结果：{result}，成功：{sc}，失败：{fc}，阻塞：{bc}\n\n'

    # 测试套件 - 测试用例结果
    txt = ''
    for k,v in testcases.items():
        txt += f'\n- ### {k}\n\n'
        txt += '| 用例id  | 用例名称 |   前置条件   |开始时间         | 结束时间       | 耗时   | 结果    |\n'
        txt += '| ------- | ------- | ----------- | -------------- | -------------- | ----- | ------- |\n'         
        for case in v:
            if case['flag'] == 'N':
                continue
            cost = round((case['end_timestamp'] - case['start_timestamp'])/1000, 1)
            result = eval(case['result'])
            txt += f'| [{case["id"]}](#{case["id"]}) | {case["title"]} | {case["condition"]} | {tm(case["start_timestamp"])} | {tm(case["end_timestamp"])} | {cost} | {result} |\n'
            
    md += f'{txt}\n\n## 测试用例执行结果\n'
    txt = ''
    for k,v in testcases.items():    
        txt += f'\n- ### {k}\n'
        for case in v:
            if case['flag'] == 'N':
                continue               
            txt += f'\n#### {case["id"]}\n\n**{case["title"]}** | {case["condition"]} | {case["designer"]} | {eval(case["result"])}\n\n'
            txt += '| 步骤  | 操作  | 页面  | 元素  | 测试数据  | 预期结果 | 输出数据  | 耗时 | 测试结果 | 备注 | 截图   |\n'
            txt += '|------|-------|-------|------|-----------|---------|-----------|-----|---------|------|--------|\n'
            for step in case['steps']:
                cost = round((step.get('end_timestamp', 0) - step.get('start_timestamp', 0))/1000, 1)
                if cost == 0:
                    cost = '-'
                if not step['score']:
                    result = skipped
                else:
                    result = eval(step['score'])
                snapshot = ''
                if 'snapshot' in step:
                    for k,v in step['snapshot'].items():
                        snapshot += f"[{k}](/report/{v} ':ignore')\n"
                txt += f'| {step["no"]} | {step["keyword"]} | {step["page"]} | {escape(step["element"])} | {escape(step["data"])} | {escape(step["expected"])} | {escape(step["output"])} | {cost} | {result} | {step["remark"]} | {escape(snapshot, "%23")} |\n'
            result = eval(case['result'])            
    md += txt            


    p = Path(md_path) / 'report'
    latest = p / 'latest'
    report = p  / g.plan_name
    mkdir(p)
    mkdir(report)


    with open(p / 'README.md', 'r', encoding='UTF-8') as f:
        txt = f.read()
        if '恭喜你安装成功' in txt:
            txt = ''
    with open(p / f'README.md', 'w', encoding='UTF-8') as f:      
        f.write(message + txt)
    with open(latest / f'{g.plan_name}.md','w', encoding='UTF-8') as f:
        f.write(md)
    readme = report / 'README.md'
    if readme.is_file():
        with open(report / 'README.md', 'r', encoding='UTF-8') as f:
            txt = f.read()
    else:
        txt = ''        
    with open(report / 'README.md','w', encoding='UTF-8') as f:
        f.write(message + txt)        
    with open(report / f'{plan["plan"]}_{tm(plan["start_timestamp"], "_")}.md','w',encoding='UTF-8') as f:
        f.write(md)
    with open(p / '_sidebar.md', 'r', encoding='UTF-8') as f:
        txt = f.read()
    if f'[{g.plan_name}]' not in txt:        
        with open(p / '_sidebar.md', 'a',encoding='UTF-8') as f:
            f.write(f'\n	* [{g.plan_name}](latest/{g.plan_name})')

    files = []
    for f in report.iterdir():
        if f.stem not in ['_sidebar', 'README']:
            files.append(f.stem)
    files.sort(reverse=True)
    with open(report / '_sidebar.md', 'w',encoding='UTF-8') as f:
        txt = f'* 「{g.plan_name}」测试结果\n'
        for stem in files: 
            txt +=f'\n    * [{stem}]({g.plan_name}/{stem})'
        f.write(txt)




def escape(data, well='#'):
    return data.replace('|', '\|').replace('<', '\<').replace('>', '\>').replace('\n', '<br>').replace('#', well)

def tm(stamp, dot=' '):
    if dot == ' ':
        return arrow.get(stamp/1000).to('local').format(f'YYYY-MM-DD{dot}HH:mm:ss').replace(':', '&#58;')
    elif dot == '_':
        return arrow.get(stamp/1000).to('local').format(f'YYYYMMDD{dot}HH:mm:ss').replace(':', '')