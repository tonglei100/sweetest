from copy import deepcopy
import requests
import json
from sweetest.globals import g
from sweetest.elements import e
from sweetest.log import logger
from sweetest.parse import data_format
from sweetest.lib.injson import in_json


class Http:

    def __init__(self, step):
        # 获取 baseurl
        el, baseurl = e.get(step['page'] + '-' + 'baseurl', True)
        if not baseurl:
            self.baseurl = ''
        else:
            if not baseurl.endswith('/'):
                baseurl += '/'
            self.baseurl = baseurl

        self.r = requests.Session()
        # 获取 headers
        el, headers = e.get(step['page'] + '-' + 'headers', True)
        if headers:
            self.r.headers.update(eval(headers))


def get(step):
    request('get', step)


def post(step):
    request('post', step)


def request(kw, step):
    element = step['element']
    el, url = e.get(element)
    if url.startswith('/'):
        url = url[1:]

    data = step['data']
    data['headers'] = data.get('headers', '')
    data['data'] = data.get('data', '{}')
    expected = step['expected']
    status_code = data.get('status_code', '')
    _text = data.get('text', '')
    _json = data.get('json', '')
    expected['status_code'] = expected.get('status_code', status_code)
    expected['text'] = expected.get('text', _text)
    expected['json'] = expected.get('json', _json)

    if not g.http.get(step['page']):
        g.http[step['page']] = Http(step)
    http = g.http[step['page']]

    logger.info('URL: \n%s' % http.baseurl + url)
    if data['headers']:
        http.r.headers.update(eval(data['headers']))
    r = getattr(http.r, kw)(http.baseurl + url, data=eval(data['data']))
    logger.info('Code: %s' % repr(r.status_code))
    logger.info('Http result: %s' % repr(r.text))

    if expected['status_code']:
        assert expected['status_code'] == str(r.status_code)

    if expected['text']:
        if expected['text'].startswith('*'):
            assert expected['text'][1:] in r.text
        else:
            assert expected['text'] == r.text

    if expected['json']:
        result = in_json(json.loads(expected['json']), r.json())
        step['remark'] += str(result['result'])
        assert result['code'] == 0


    output = step['output']
    if output:
        logger.info('output: %s' % repr(output))
        # TODO
        # for key in output:
        #     g.var[key] = r.json[output[key]]
