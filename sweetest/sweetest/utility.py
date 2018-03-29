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
            raise Error('Error: init Excel class with error mode: %s' % mode)

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
            raise Error('Error: invalidity sheet_name: %s' % sheet_name)

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
    key = data[0]
    for d in data[1:]:
        dict_data = {}
        for i in range(len(key)):
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
            data = data.replace('<' + k + '>', g.var[k])
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
    for d in data[1:]:
        if d[-1] != 'Y':
            for i in range(len(data[0][:-1])):
                record[data[0][i]] = d[i]

            d[-1] = 'Y'
            write_csv(data_file, data)
    return record
