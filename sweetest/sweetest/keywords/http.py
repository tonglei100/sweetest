from copy import deepcopy
import requests
from sweetest.globals import g
from sweetest.elements import e
from sweetest.log import logger
from sweetest.parse import data_format


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


def json_in_test(sub, parent):
    # TODO
    return True


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
    data['status_code'] = data.get('status_code', '')
    data['text'] = data.get('text', '')
    data['json'] = data.get('json', '')

    if not g.http.get(step['page']):
        g.http[step['page']] = Http(step)
    http = g.http[step['page']]

    logger.info('URL: \n%s' % http.baseurl + url)
    if data['headers']:
        http.r.headers.update(eval(data['headers']))
    r = getattr(http.r, kw)(http.baseurl + url, data=eval(data['data']))
    logger.info('Code: %s' % r.status_code)
    logger.info('Http result: %s' % (r.text,))

    if data['status_code']:
        assert data['status_code'] == str(r.status_code)

    if data['text'].startswith('*'):
        assert data['text'][1:] in r.text
    else:
        assert data['text'] == r.text

    if data['json']:
        assert json_in_test(data['json'], r.json())

    output = step['output']
    if output:
        logger.info('output: %s' % output)
        # TODO
        # for key in output:
        #     g.var[key] = r.json[output[key]]
