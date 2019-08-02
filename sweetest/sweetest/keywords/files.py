import os
from sweetest.log import logger


def copy(step):
    cwd = os.getcwd()
    source = step['element']
    destination = step['data']['text']

    if step['page']: 
        os.chdir(step['page'])

    code = 0
    if os.name == 'nt':
        code = os.system(f'COPY /Y {source} {destination}')
    if os.name == 'posix':
        code = os.system(f'cp -f -R {source} {destination}')    

    if step['page']: 
        os.chdir(cwd)

    if code != 0:
        raise Exception(f'COPY {source} {destination} is failure, code: {code}')


def move(step):
    cwd = os.getcwd()
    source = step['element']
    destination = step['data']['text']

    if step['page']: 
        os.chdir(step['page'])

    code = 0
    if os.name == 'nt':
        code = os.system(f'MOVE /Y {source} {destination}')
    if os.name == 'posix':
        code = os.system(f'mv -f {source} {destination}')    

    if step['page']: 
        os.chdir(cwd)

    if code != 0:
        raise Exception(f'MOVE {source} {destination} is failure, code: {code}')


def remove(step):
    cwd = os.getcwd()
    path = step['element']

    if step['page']: 
        os.chdir(step['page'])

    code = 0
    if os.name == 'nt':
        code = os.system(f'del /S /Q {path}')
    if os.name == 'posix':
        code = os.system(f'rm -f {path}')    

    if step['page']: 
        os.chdir(cwd)

    if code != 0:
        raise Exception(f'REMOVE {path} is failure, code: {code}')


def rmdir(step):
    cwd = os.getcwd()
    path = step['element']

    if step['page']: 
        os.chdir(step['page'])

    code = 0
    if os.name == 'nt':
        code = os.system(f'rd /S /Q {path}')
    if os.name == 'posix':
        code = os.system(f'rm -rf {path}')    

    if step['page']: 
        os.chdir(cwd)

    if code != 0:
        raise Exception(f'RERMDIR {path} is failure, code: {code}')


def mkdir(step):
    cwd = os.getcwd()
    path = step['element']

    if step['page']: 
        os.chdir(step['page'])

    code = 0
    if os.name == 'nt':
        code = os.system(f'mkdir {path}')
    if os.name == 'posix':
        code = os.system(f'mkdir -p {path}')    

    if step['page']: 
        os.chdir(cwd)

    if code != 0:
        raise Exception(f'MKDIR {path} is failure, code: {code}')


def exists(step):
    cwd = os.getcwd()
    path = step['element']

    if step['page']: 
        os.chdir(step['page'])

    result = os.path.exists(path)

    if step['page']: 
        os.chdir(cwd)

    if not result:
        raise Exception(f'{path} is not exists')    


def not_exists(step):
    try:
        exists(step)
    except:
        pass
    else:
        path = step['element']
        raise Exception(f'{path} is a exists')
    

def is_file(step):
    cwd = os.getcwd()
    path = step['element']

    if step['page']: 
        os.chdir(step['page'])

    result = os.path.isfile(path)

    if step['page']: 
        os.chdir(cwd)

    if not result:
        raise Exception(f'{path} is not file')


def not_file(step):
    try:
        is_file(step)
    except:
        pass
    else:
        path = step['element']
        raise Exception(f'{path} is a file')

        
def is_dir(step):
    cwd = os.getcwd()
    path = step['element']

    if step['page']: 
        os.chdir(step['page'])

    result = os.path.isdir(path)

    if step['page']: 
        os.chdir(cwd)

    if not result:
        raise Exception(f'{path} is not dir')


def not_dir(step):
    try:
        is_dir(step)
    except:
        pass
    else:
        path = step['element']
        raise Exception(f'{path} is a dir')


def command(step, name=None):
    cwd = os.getcwd()
    cmd = step['element']

    if name and os.name != name:
        logger.info(f'COMMAND: this OS is not {name}, "{cmd}" is skipped')
        return


    if step['page']: 
        os.chdir(step['page'])

    code = os.system(cmd)  

    if step['page']: 
        os.chdir(cwd)

    if code != 0:
        raise Exception(f'COMMAND: "{cmd}" is failure, code: {code}')


def shell(step):
    command(step, 'posix')


def cmd(step):
    command(step, 'nt')