import xlrd
import xlsxwriter
import csv
from sweetest.config import header
from sweetest.globals import g


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
    # 变量替换
    if '>' in data:
        for k in g.var:
            if isinstance(g.var[k], list):
                if '<' + k + '>' in data:
                    data = data.replace('<' + k + '>', str(g.var[k].pop(0)))
                    if len(g.var[k]) == 1:
                        g.var[k] = g.var[k][0]
            else:
                data = data.replace('<' + k + '>', str(g.var[k]))
    return data


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
    if s[-1] == '0':
        s = s[:-1]
        s = zero(s)
    return s


def str2float(s):
    s = s.replace(',', '').split('.', 1)
    dot = '0'
    if len(s) == 2:
        dot = s[-1]
        dot = zero(dot)
    f = float(s[0]+'.'+dot)
    return round(f, len(dot)), len(dot)
