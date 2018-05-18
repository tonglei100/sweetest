from sweetest.autotest import Autotest

# 项目名称，和测试用例、页面元素表文件名称中的项目名称必须一致
project_name = 'Baidu'

# 单 sheet 页面模式
sheet_name = 'baidu'

# sheet 页面匹配模式，仅支持结尾带*
#sheet_name = 'TestCase*'

# #sheet 页面列表模式
#sheet_name = ['TestCase', 'test']

# 环境配置信息
# Chrome
# desired_caps = {'platformName': 'Desktop', 'app': 'Chrome'}
# server_url = ''


# 执行
test = Autotest(project_name, sheet_name)
# 如果需要指定环境信息，则执行如下语句
#test = Autotest(project_name, sheet_name, desired_caps, server_url)

test.plan()
