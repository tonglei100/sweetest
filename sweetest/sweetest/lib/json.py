from copy import deepcopy


def code_sort(data):
    result = []
    for k,v in data.items():
        result.append(v['code'])
    return  result


def optimum(sub, result, path):
    if path != '/':
        path += '.'

    res = result
    for k in sub:
        result = deepcopy(res)
        temp = res
        res = []
        flag = False
        for data in result:
            if path + k not in data:
                flag = True
                res.append(data)
        if not flag:
            temp.sort(key=lambda d: code_sort(d))
            return temp[0]
    result.sort(key=lambda d: code_sort(d))
    return result[0]


def in_json(sub, parent,  spath='/', ppath='/'):  # '/result[1].sweetest'
    re = {'code': 0, 'result': {}}
    if spath != '/':
        spath += '.'
    if ppath != '/':
        ppath += '.'

    for k, sv in sub.items():
        if k in parent:
            pv = parent[k]
            code = 0
            if isinstance(sv, str):
                if not (isinstance(pv, str) and sv == pv):
                    code = 1  # 键值不等

            elif isinstance(sv, int):
                # TODO pv 类型判断
                if not (isinstance(pv, int) and sv == pv):
                    code = 1  # 键值不等

            elif isinstance(sv, float):
                # TODO pv 类型判断
                if not (absisinstance(pv, float) and sv == pv):
                    code = 1  # 键值不等

            elif isinstance(sv, list):
                if not isinstance(pv, list):
                    code = 2  # 键值的数据类型不一致
                elif not isinstance(sv[0], dict):
                    if  sv != pv:
                        code = 1  # 键值不等
                else:
                    for i,sv_i in enumerate(sv):
                        result = []
                        flag = False
                        for j,pv_i in enumerate(pv):
                            r = in_json(
                                sv_i, pv_i, spath + k + '[%s]' % i, ppath + k + '[%s]' % j)
                            if r['code'] == 0:
                                # code = 0
                                flag = True
                                break
                            else:
                                result.append(r['result'])
                        o = optimum(sv_i, result, spath + k + '[%s]' % i)

                        if not flag:
                            re['code'] = 1
                            re['result'] = dict(re['result'], **o)

            elif isinstance(sv, dict):
                if not isinstance(pv, dict):
                    code = 2  # 键值的数据类型不一致
                else:
                    r = in_json(
                        sv, pv, spath + k, ppath + k)
                    if r['code'] != 0:
                        re['result'][spath + k] = r['result']

            if code == 1:
                re['code'] = 1
                re['result'][spath + k] = {'code': 1, 'sv': sv, 'ppath': ppath + k, 'pv': pv}
            elif code == 2:
                re['code'] = 2
                re['result'][spath + k]  = {'code': 2, 'sv': v, 'ppath': ppath + k, 'pv': ''}
        else:
            re['code'] = 3
            re['result'][spath + k]  = {'code': 3, 'sv': sv, 'ppath': None, 'pv': ''}

    re['code'] = len(re['result'])
    return re


def test():
    sub = {"code":200,
            "error": "hello,word",
            "result": [
                {"sweetest":"OK",
                 "status": "yes"
                },
                {"ages":[1,2,4],
                 "status": "yes"
                },
                {"sonar":"OK",
                 "status": "yes"
                }
            ],
           }

    parent = {"code":200,
            "error": "you are bad",
            "result": [
                {"sweetest":"Fail",
                 "status": "NO"
                },
                {"sweetest":"OK",
                 "status": "NO"
                },
                {"ages":[1,2,3],
                 "status": "yes"
                },
                {"sonar":"OK",
                 "status": "yes"
                }
            ],
           }

    result = in_json(sub, parent)

    print('result:\n%s\n' %result)

    print('code: %s' %result['code'])
    re = result['result']
    for k in re:
        print('\n%s: %s' %(k, re[k]['sv']))
        print('%s: %s' %(re[k]['ppath'], re[k]['pv']))


if __name__ == '__main__':
    test()
