import os


keywords = {
    '复制': 'COPY',
    'COPY': 'COPY',
    '移动': 'MOVE',
    'MOVE': 'MOVE',
    '删除文件': 'REMOVE',
    'REMOVE': 'REMOVE',
    '删除目录': 'RMDIR',
    'RMDIR': 'RMDIR',
    '创建目录': 'MKDIR',
    'MKDIR': 'MKDIR',
    '路径存在': 'EXISTS',
    'EXISTS': 'EXISTS',
    '路径不存在': 'NOT_EXISTS',
    'NOT_EXISTS': 'NOT_EXISTS',
    '是文件': 'IS_FILE',
    'IS_FILE': 'IS_FILE',
    '是目录': 'IS_DIR',
    'IS_DIR': 'IS_DIR',
    '不是文件': 'NOT_FILE',
    'NOT_FILE': 'NOT_FILE',
    '不是目录': 'NOT_DIR',
    'NOT_DIR': 'NOT_DIR'
}


class App:

    keywords = keywords

    def __init__(self, setting):
        self.dir = '.'
        if 'dir' in setting:
            self.dir = setting['dir']
            os.chdir(self.dir)

    def _close(self):
        pass

    def _call(self, step):
        # 根据关键字调用关键字实现
        getattr(self, step['keyword'].lower())(step)


    def copy(self, step):
        source = step['element']
        data = step['data']
        destination = data['text']

        if 'dir' in data:
            os.chdir(data['dir'])
        else:
            os.chdir(self.dir)

        code = 0
        if os.name == 'nt':
            code = os.system(f'COPY /Y {source} {destination}')
        if os.name == 'posix':
            code = os.system(f'cp -f -R {source} {destination}')

        if code != 0:
            raise Exception(
                f'COPY {source} {destination} is failure, code: {code}')

    def move(self, step):
        source = step['element']
        data = step['data']
        destination = data['text']

        if 'dir' in data:
            os.chdir(data['dir'])
        else:
            os.chdir(self.dir)

        code = 0
        if os.name == 'nt':
            code = os.system(f'MOVE /Y {source} {destination}')
        if os.name == 'posix':
            code = os.system(f'mv -f {source} {destination}')

        if code != 0:
            raise Exception(
                f'MOVE {source} {destination} is failure, code: {code}')

    def remove(self, step):
        path = step['element']
        data = step['data']

        if 'dir' in data:
            os.chdir(data['dir'])
        else:
            os.chdir(self.dir)

        code = 0
        if os.name == 'nt':
            code = os.system(f'del /S /Q {path}')
        if os.name == 'posix':
            code = os.system(f'rm -f {path}')

        if code != 0:
            raise Exception(f'REMOVE {path} is failure, code: {code}')

    def rmdir(self, step):
        path = step['element']
        data = step['data']

        if 'dir' in data:
            os.chdir(data['dir'])
        else:
            os.chdir(self.dir)

        code = 0
        if os.name == 'nt':
            code = os.system(f'rd /S /Q {path}')
        if os.name == 'posix':
            code = os.system(f'rm -rf {path}')

        if code != 0:
            raise Exception(f'RERMDIR {path} is failure, code: {code}')

    def mkdir(self, step):
        path = step['element']
        data = step['data']

        if 'dir' in data:
            os.chdir(data['dir'])
        else:
            os.chdir(self.dir)

        code = 0
        if os.name == 'nt':
            code = os.system(f'mkdir {path}')
        if os.name == 'posix':
            code = os.system(f'mkdir -p {path}')

        if code != 0:
            raise Exception(f'MKDIR {path} is failure, code: {code}')

    def exists(self, step):
        path = step['element']
        result = os.path.exists(path)

        if not result:
            raise Exception(f'{path} is not exists')

    def not_exists(self, step):
        try:
            self.exists(step)
        except:
            pass
        else:
            path = step['element']
            raise Exception(f'{path} is a exists')

    def is_file(self, step):
        path = step['element']

        result = os.path.isfile(path)

        if not result:
            raise Exception(f'{path} is not file')

    def not_file(self, step):
        try:
            self.is_file(step)
        except:
            pass
        else:
            path = step['element']
            raise Exception(f'{path} is a file')

    def is_dir(self, step):
        path = step['element']

        result = os.path.isdir(path)

        if not result:
            raise Exception(f'{path} is not dir')

    def not_dir(self, step):
        try:
            self.is_dir(step)
        except:
            pass
        else:
            path = step['element']
            raise Exception(f'{path} is a dir')
