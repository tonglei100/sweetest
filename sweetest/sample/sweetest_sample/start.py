from sweetest.autotest import Autotest

# 单 sheet 页面模式
test = Autotest('Baidu', 'baidu')
test.plan()


# sheet 页面匹配模式，仅支持结尾带*
#test = Autotest('Baidu', 'bai*')
#test.plan()


# #sheet 页面列表模式
#test = Autotest('Baidu', ['baidu'])
#test.plan()
