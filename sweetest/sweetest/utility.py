import xlrd
import xlsxwriter
import csv
import re
from sweetest.config import header
from sweetest.globals import g
from sweetest.lib import *


class Excel:
    def __init__(self, file_name, mode='r'):
        if mode == 'r':
            self.workbook = xlrd.open_workbook(file_name)
        elif mode == 'w':
            self.workbook = xlsxwriter.Workbook(file_name)
        else:
            raise Exception(
                'Error: init Excel class with error mode: %s' % mode)

    def get_sheet(self, sheet_name):
        names = []
        if isinstance(sheet_name, str):
            if sheet_name.endswith('*'):
                for name in self.workbook.sheet_names():
                    if sheet_name[:-1] in name:
                        names.append(name)
            else:
                names.append(sheet_name)
        elif isinstance(sheet_name, list):
            names = sheet_name
        else:
            raise Exception('Error: invalidity sheet_name: %s' % sheet_name)

        return names

    def read(self, sheet_name):
        '''
        sheet_name:Excel 中标签页名称
        return：[[],[]……]
        '''
        sheet = self.workbook.sheet_by_name(sheet_name)
        nrows = sheet.nrows
        data = []
        for i in range(nrows):
            data.append(sheet.row_values(i))
        return data

    def write(self, data, sheet_name):
        sheet = self.workbook.add_worksheet(sheet_name)

        red = self.workbook.add_format({'bg_color': 'red', 'color': 'white'})
        yellow = self.workbook.add_format(
            {'bg_color': 'yellow', 'color': 'black'})
        gray = self.workbook.add_format({'bg_color': 'gray', 'color': 'white'})
        green = self.workbook.add_format(
            {'bg_color': 'green', 'color': 'white'})
        blue = self.workbook.add_format({'bg_color': 'blue', 'color': 'white'})
        orange = self.workbook.add_format(
            {'bg_color': 'orange', 'color': 'white'})
        for i in range(len(data)):
            for j in range(len(data[i])):
                if str(data[i][j]) == 'Fail':
                    sheet.write(i, j, str(data[i][j]), red)
                elif str(data[i][j]) == 'NO':
                    sheet.write(i, j, str(data[i][j]), gray)
                elif str(data[i][j]) == 'Block':
                    sheet.write(i, j, str(data[i][j]), orange)
                elif str(data[i][j]) == 'Skip':
                    sheet.write(i, j, str(data[i][j]), blue)
                elif str(data[i][j]) == 'Pass':
                    sheet.write(i, j, str(data[i][j]), green)
                else:
                    sheet.write(i, j, str(data[i][j]))

    def close(self):
        self.workbook.close()


def data2dict(data):
    # def list_list2list_dict(data):
    '''
    把带头标题的二维数组，转换成以标题为 key 的 dict  的 list
    '''
    list_dict_data = []
    key = []
    g.header_custom = {}  # 用户自定义的标题
    for d in data[0]:
        k = d.strip().split('#')[0]
        # 如果为中文，则替换成英文
        h = header.get(k, k).lower()
        key.append(h)
        g.header_custom[h] = d.strip()

    if not g.header_custom.get('expected'):
        g.header_custom['expected'] = ''

    for d in data[1:]:
        dict_data = {}
        for i in range(len(key)):
            if isinstance(d[i], str):
                dict_data[key[i]] = str(d[i]).strip()
            else:
                dict_data[key[i]] = d[i]
        list_dict_data.append(dict_data)
    return list_dict_data


def replace_dict(data):
    # 变量替换
    for key in data:
        data[key] = replace(data[key])


def replace_list(data):
    # 变量替换
    for i in range(len(data)):
        data[i] = replace(data[i])


def replace(data):
    # 正则匹配出 data 中所有 <> 中的变量，返回列表
    keys = re.findall(r'<(.*?)>', data)
    for i,k in enumerate(keys):
        # 正则匹配出 k 中的 + - ** * // / % ( )，返回列表
        values = re.split(r'(\+|-|\*\*|\*|//|/|%|\(|\))', k)
        for j,v in enumerate(values):
            # 切片操作处理，正在匹配出 [] 中内容
            s = re.findall(r'\[.*?\]', v)
            if s:
                s = s[0]
                v = v.replace(s, '')

            if v in g.var:
                # 如果在 g.var 中是 list，则 pop 第一个值
                if isinstance(g.var[v], list):
                    values[j] = g.var[k].pop(0)
                    if s:
                        values[j] = eval('values[j]'+s)
                    # 再判断一下此 list 是否只有一个值了，如果是，则从 list 变为该值
                    if len(g.var[v]) == 1:
                        g.var[v] = g.var[v][0]
                # 如果在 g.var 中是值，则直接赋值
                else:
                    values[j] = g.var[v]
                    if s:
                        values[j] = eval('values[j]'+s)

        #如果 values 长度大于 1，说明有算术运算符，则用 eval 运算
        # 注意，先要把元素中的数字变为字符串
        if len(values) > 1:
            values = eval(''.join([str(x) for x in values]))
        # 如果 values 长度为 1，则直接赋值，注意此值可能是数字
        else:
            values = values[0]
        # 如果 data 就是一个 <>，如 data = '<a+1>',则直接赋值为 values，此值可能是数字
        if data == '<' + keys[0] + '>':
            data = values
        # 否则需要替换，此时变量强制转换为为字符串
        else:
            data = data.replace('<' + k + '>', str(values))
    return data


def test_replace():
    g.var = {'a': 1, 'b': 'B'}
    for d in ('<a+1>','<b>','abc<a>', 'abc<a+1>', '<a*(8+4)/2//3>', '<u.td(-3)>'):
        print('data:%s' %d)
        data = replace(d)
        print(repr(data))


def read_csv(csv_file):
    data = []
    with open(csv_file) as f:
        reader = csv.reader(f)
        for line in reader:
            data.append(line)
    return data


def write_csv(csv_file, data):
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)


def get_record(data_file):
    data = read_csv(data_file)
    record = {}
    if data[0][-1].lower() != 'flag':
        for d in data[1:]:
            for i in range(len(data[0])):
                k = data[0][i]
                if record.get(k, None):
                    if isinstance(record[k], str):
                        record[k] = [record[k]]
                    record[k].append(d[i])
                else:
                    record[k] = d[i]

    else:
        for d in data[1:]:
            if d[-1] != 'Y':
                for i in range(len(data[0][:-1])):
                    k = data[0][i]
                    if record.get(k, None):
                        if isinstance(record[k], str):
                            record[k] = [record[k]]
                        record[k].append(d[i])
                    else:
                        record[k] = d[i]
                d[-1] = 'Y'
                write_csv(data_file, data)
                break
    return record


def str2int(s):
    s = s.replace(',', '').split('.', 1)
    if len(s) == 2:
        dot = s[-1]
        assert int(dot) == 0
    return int(s[0])


def zero(s):
    if s and s[-1] == '0':
        s = s[:-1]
        s = zero(s)
    return s


def str2float(s):
    s = str(s).replace(',', '').split('.', 1)
    dot = '0'
    if len(s) == 2:
        dot = s[-1]
        dot = zero(dot)
    f = float(s[0]+ '.' +dot)

    return round(f, len(dot)), len(dot)
