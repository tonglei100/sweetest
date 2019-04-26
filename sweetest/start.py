from sweetest import Autotest
import sys


# 项目名称，和测试用例、页面元素表文件名称中的项目名称必须一致
plan_name = 'Baidu'

# 单 sheet 页面模式
sheet_name = 'baidu'

# sheet 页面匹配模式，仅支持结尾带*
#sheet_name = 'TestCase*'

# sheet 页面列表模式
#sheet_name = ['TestCase', 'test']

# 环境配置信息
# Chrome
desired_caps = {'platformName': 'Desktop', 'browserName': 'Chrome'}
# headless
#desired_caps = {'platformName': 'Desktop', 'browserName': 'Chrome', 'headless': True}
# 设置全局截图
#desired_caps = {'platformName': 'Desktop', 'browserName': 'Chrome', 'snapshot': True}
# 指定 driver 路径
#desired_caps = {'platformName': 'Desktop', 'browserName': 'Chrome', 'executable_path': 'D:\drivers\chromedriver.exe'}
server_url = ''

# Windows GUI
# notepad start
#desired_caps = {'platformName': 'Windows', 'cmd_line': r'notepad.exe', 'timeout': 5, 'backend': 'uia'}
# notepad connect
#desired_caps = {'platformName': 'Windows', 'path': r'C:\Program Files\Microsoft Office\Office16\EXCEL.EXE'}

# 初始化自动化实例
sweet = Autotest(plan_name, sheet_name, desired_caps, server_url)

# 按条件执行,支持筛选的属性有：'id', 'title', 'designer', 'priority'
# sweet.fliter(priority='H')

# 执行自动化测试
sweet.plan()

#group = WEB
#project = Baidu
#测试报告详细数据，可以自行处理后写入其他测试报告系统
#print(sweet.report_data)

# 如果是集成到 CI/CD，则给出退出码
#sys.exit(sweet.code)
