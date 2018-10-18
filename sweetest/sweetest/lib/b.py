
def before_send(data, kwargs):
    '''
    data: dict，格式如下：
        {'headers':{},
         'params': {},
         'data': {},
         'json': {},
         'files': 'file path'
        }

    keargs: dict，其他参数
    '''
    # handle the request here

    return data, kwargs

def after_receive(response):
    '''
    response: dict, 格式如下：
    {'status_code': 200,
     'headers': {},
     '_cookies': '',  # 原始内容
     'cookies': {},   # dict 格式
     'content': b'',
     'text': '',
     'json': {}
     }
    '''
    # handle the response here

    return response
