import os
import sys
import shutil
import zipfile


def extract(zfile, path):
    f = zipfile.ZipFile(zfile, 'r')
    for file in f.namelist():
        f.extract(file, path)


def sweetest():
    sweetest_dir = os.path.dirname(os.path.realpath(__file__))
    example_dir = os.path.join(sweetest_dir, 'example')
    current_dir = os.getcwd()
    extract(os.path.join(example_dir, 'sweetest_example.zip'), current_dir)

    print('\n生成 sweetest example 成功\n\n详细使用说明请关注公众号：Sweetest自动化测试\nQQ交流群：158755338 (验证码：python)')
    print('\n\n快速体验，请输入如下命令，进入示例目录，启动运行脚本\n\ncd sweetest_example\npython start.py')
