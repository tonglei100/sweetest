import sys
import shutil
import zipfile
from pathlib import Path

def extract(zfile, path):
    f = zipfile.ZipFile(zfile, 'r')
    for file in f.namelist():
        f.extract(file, path)


def sweetest():
    sweetest_dir = Path(__file__).resolve().parents[0]
    example_dir = sweetest_dir /'example'
    extract(example_dir / 'sweetest_example.zip', Path.cwd())

    print('\n生成 sweetest example 成功\n\n详细使用说明请关注公众号：Sweetest自动化测试\nQQ交流群：158755338 (验证码：python)')
    print('\n\n快速体验，请输入如下命令，进入示例目录，启动运行脚本\n\ncd sweetest_example\npython start.py')
