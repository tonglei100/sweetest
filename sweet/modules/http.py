import requests
from pathlib import Path
from injson import check

from sweet import log, vars
from sweet.utility import json2dict


path = Path('lib') / 'http_handle.py'
if path.is_file():
    from lib import http_handle
else:
    from sweet.lib import http_handle


keywords = {
    'GET': 'GET',
    'POST': 'POST',
    'PUT': 'PUT',
    'PATCH': 'PATCH',
    'DELETE': 'DELETE',
    'OPTIONS': 'OPTIONS'
}


class App:

    keywords = keywords

    def __init__(self, setting):
        # 获取 path
        self.path = setting.get('path', '')
        if self.path:
            if not self.path.endswith('/'):
                self.path += '/'

        self.r = requests.Session()

        # 获取 headers
        self.headers = {}
        for key in keywords:
            if setting.get(key.lower()):
                self.headers[key.upper()] = setting.get(key.lower())


    def _close(self):
        self.r.close()

    def _call(self, step):
        # 根据关键字调用关键字实现
        getattr(self, step['keyword'].lower())(step)


    def get(self, step):
        self.request('get', step)

    def post(self, step):
        self.request('post', step)

    def put(self, step):
        self.request('put', step)

    def patch(self, step):
        self.request('patch', step)

    def delete(self, step):
        self.request('delete', step)

    def options(self, step):
        self.request('options', step)


    def request(self, kw, step):
        url = step['element']
        if url.startswith('/'):
            url = url[1:]

        data = step['data']
        # 测试数据解析时，会默认添加一个 text 键，需要删除
        if 'text' in data and not data['text']:
            data.pop('text')

        _data = {}
        _data['headers'] = json2dict(data.pop('headers', '{}'))
        if data.get('cookies'):
            data['cookies'] = json2dict(data['cookies'])
        if kw == 'get':
            _data['params'] = json2dict(
                data.pop('params', '{}')) or json2dict(data.pop('data', '{}'))
        elif kw == 'post':
            if data.get('text'):
                _data['data'] = data.pop('text').encode('utf-8')
            else:
                _data['data'] = json2dict(data.pop('data', '{}'))
            _data['json'] = json2dict(data.pop('json', '{}'))
            _data['files'] = eval(data.pop('files', 'None'))
        elif kw in ('put', 'patch'):
            _data['data'] = json2dict(data.pop('data', '{}'))

        for k in data:
            for s in ('{', '[', 'False', 'True'):
                if s in data[k]:
                    try:
                        data[k] = eval(data[k])
                    except:
                        log.warning(f'try eval data failure: {data[k]}')
                    break
        expected = step['expected']
        expected['status_code'] = expected.get('status_code', None)
        expected['text'] = expected.get('text', '').encode('utf-8')
        expected['json'] = json2dict(expected.get('json', '{}'))
        expected['cookies'] = json2dict(expected.get('cookies', '{}'))
        expected['headers'] = json2dict(expected.get('headers', '{}'))
        timeout = float(expected.get('timeout', 10))
        expected['time'] = float(expected.get('time', 0))

        for key in keywords:
            if kw.upper() == key.upper():
                self.r.headers.update(self.headers[key.upper()])

        log.debug(f'URL: {self.path + url}')

        # 处理 before_send
        before_send = data.pop('before_send', '')
        if before_send:
            _data, data = getattr(http_handle, before_send)(kw, _data, data)
        else:
            _data, data = getattr(http_handle, 'before_send')(kw, _data, data)

        if _data['headers']:
            for k in [x for x in _data['headers']]:
                if not _data['headers'][k]:
                    del self.r.headers[k]
                    del _data['headers'][k]
            self.r.headers.update(_data['headers'])

        r = ''
        if kw == 'get':
            r = getattr(self.r, kw)(self.path + url,
                                    params=_data['params'], timeout=timeout, **data)
            if _data['params']:
                log.debug(f'PARAMS: {_data["params"]}')

        elif kw == 'post':
            r = getattr(self.r, kw)(self.path + url,
                                    data=_data['data'], json=_data['json'], files=_data['files'], timeout=timeout, **data)
            log.debug(f'BODY: {r.request.body}')

        elif kw in ('put', 'patch'):
            r = getattr(self.r, kw)(self.path + url,
                                    data=_data['data'], timeout=timeout, **data)
            log.debug(f'BODY: {r.request.body}')

        elif kw in ('delete', 'options'):
            r = getattr(self.r, kw)(self.path + url, timeout=timeout, **data)

        log.debug(f'status_code: {repr(r.status_code)}')
        try:  # json 响应
            log.debug(f'response json: {repr(r.json())}')
        except:  # 其他响应
            log.debug(f'response text: {repr(r.text)}')

        response = {'status_code': r.status_code, 'headers': r.headers,
                    '_cookies': r.cookies, 'content': r.content, 'text': r.text}

        try:
            response['cookies'] = requests.utils.dict_from_cookiejar(r.cookies)
        except:
            response['cookies'] = r.cookies

        try:
            j = r.json()
            response['json'] = j
        except:
            response['json'] = {}

        # 处理 after_receive
        after_receive = expected.pop('after_receive', '')
        if after_receive:
            response = getattr(http_handle, after_receive)(response)
        else:
            response = getattr(http_handle, 'after_receive')(response)

        if expected['status_code']:
            if str(expected['status_code']) != str(response['status_code']):
                raise Exception(
                    f'status_code | EXPECTED:{repr(expected["status_code"])}, REAL:{repr(response["status_code"])}')

        if expected['text']:
            if expected['text'].startswith('*'):
                if expected['text'][1:] not in response['text']:
                    raise Exception(
                        f'text | EXPECTED:{repr(expected["text"])}, REAL:{repr(response["text"])}')
            else:
                if expected['text'] == response['text']:
                    raise Exception(
                        f'text | EXPECTED:{repr(expected["text"])}, REAL:{repr(response["text"])}')

        if expected['headers']:
            result = check(expected['headers'], response['headers'])
            log.debug(f'headers check result: {result}')
            if result['code'] != 0:
                raise Exception(
                    f'headers | EXPECTED:{repr(expected["headers"])}, REAL:{repr(response["headers"])}, RESULT: {result}')
            elif result['var']:
                # var.update(result['var'])
                vars.put(result['var'])
                log.debug(f'headers var: {repr(result["var"])}')

        if expected['cookies']:
            log.debug(f'response cookies: {response["cookies"]}')
            result = check(expected['cookies'], response['cookies'])
            log.debug(f'cookies check result: {result}')
            if result['code'] != 0:
                raise Exception(
                    f'cookies | EXPECTED:{repr(expected["cookies"])}, REAL:{repr(response["cookies"])}, RESULT: {result}')
            elif result['var']:
                # var.update(result['var'])
                vars.put(result['var'])
                log.debug(f'cookies var: {repr(result["var"])}')

        if expected['json']:
            result = check(expected['json'], response['json'])
            log.debug(f'json check result: {result}')
            if result['code'] != 0:
                raise Exception(
                    f'json | EXPECTED:{repr(expected["json"])}, REAL:{repr(response["json"])}, RESULT: {result}')
            elif result['var']:
                # var.update(result['var'])
                vars.put(result['var'])
                log.debug(f'json var: {repr(result["var"])}')

        if expected['time']:
            if expected['time'] < r.elapsed.total_seconds():
                raise Exception(
                    f'time | EXPECTED:{repr(expected["time"])}, REAL:{repr(r.elapsed.total_seconds())}')

        output = step['output']
        # if output:
        #     log.debug('output: %s' % repr(output))

        for k, v in output.items():
            if v == 'status_code':
                status_code = response['status_code']
                vars.put({k: status_code})
                log.debug(f'{k}: {status_code}')
            elif v == 'text':
                text = response['text']
                vars.put({k: text})
                log.debug(f'{k}: {text}')
            elif k == 'json':
                sub = json2dict(output.get('json', '{}'))
                result = check(sub, response['json'])
                # var.update(result['var'])
                vars.put(result['var'])
                log.debug(f'json var: {repr(result["var"])}')
            elif k == 'cookies':
                sub = json2dict(output.get('cookies', '{}'))
                result = check(sub, response['cookies'])
                vars.put(result['var'])
                log.debug(f'cookies var: {repr(result["var"])}')
