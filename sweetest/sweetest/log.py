import logging
import datetime
from os import path


def today():
    now = datetime.datetime.now()
    return now.strftime('%Y%m%d')


logname = path.join('log', '%s.log' % today())
filehandler = logging.FileHandler(filename=logname,encoding="utf-8")
fmter = logging.Formatter(fmt='%(asctime)s [%(levelname)s] %(filename)s line:%(lineno)d: %(message)s')
filehandler.setFormatter(fmter)

# logging.basicConfig(format='%(asctime)s [%(levelname)s] %(filename)s line:%(lineno)d %(funcName)s: %(message)s', filename=path.join(
# 'log', '%s.log' % today()), level=logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(filename)s line:%(lineno)d: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logging.getLogger('').addHandler(filehandler)
logging.getLogger('').setLevel(logging.DEBUG)
