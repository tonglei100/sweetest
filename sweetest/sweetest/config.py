keywords_map = {
    '打开': 'OPEN',
    'OPEN': 'OPEN',
    '检查': 'CHECK',
    'CHECK': 'CHECK',
    '#检查': 'NOTCHECK',
    '#CHECK': 'NOTCHECK',
    '输入': 'INPUT',
    'INPUT': 'INPUT',
    '点击': 'CLICK',
    'CLICK': 'CLICK',
    '选择': 'SELECT',
    'SELECT': 'SELECT',
    '移动到': 'MOVE',
    'MOVE': 'MOVE',
    '执行': 'EXECUTE',
    'EXECUTE': 'EXECUTE'
}

#文件名么后缀
_testcase = 'TestCase'  #'测试用例'
_elements = 'Elements'  #'页面元素表'
_report = 'Report'  #'测试结果'

comma_lower = '#$%^&'
comma_upper = '&^%$#'
equals = '%^$#&'
vertical = '&$&*^&A@'

header = ['用例编号', '用例标题', '前置条件', '步骤编号', '操作', '页面', '元素',
          '测试数据', '输出数据', '优先级', '设计者', '自动化标记',	'测试结果', '备注']

element_wait_imeout = 30  # 等待元素出现超时时间，单位：秒
page_flash_timeout = 90 # 页面刷新超时时间，单位：秒
