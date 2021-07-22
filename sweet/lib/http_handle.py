# 本文件为 Http 测试调用，请勿修改名称。

def before_send(method, data, kwargs):
    '''
    method: str, 请求类型 
    值可以为：post, get, put, patch, delete, options

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
