import os
import sys
import shutil
import zipfile

def extract(zfile, path):
    f = zipfile.ZipFile(zfile,'r')
    for file in f.namelist():
        f.extract(file, path)


def sweetest():
    sweetest_dir = os.path.dirname(os.path.realpath(__file__))
    example_dir = os.path.join(sweetest_dir,'example')
    current_dir = os.getcwd()
    extract(os.path.join(example_dir, 'sweetest_example.zip'), current_dir)

    print('生成 sweetest example 成功')
