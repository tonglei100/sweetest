
web_keywords = {
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
    '右击': 'CONTEXT_CLICK',
    'CONTEXT_CLICK': 'CONTEXT_CLICK',
    '双击': 'DOUBLE_CLICK',
    'DOUBLE_CLICK': 'DOUBLE_CLICK',
    '拖拽': 'DRAG_AND_DROP',
    'DRAG_AND_DROP': 'DRAG_AND_DROP',
    '滑动': 'SWIPE',
    'SWIPE': 'SWIPE',
    '脚本': 'SCRIPT',
    'SCRIPT': 'SCRIPT',
    '对话框': 'MESSAGE',
    'MESSAGE': 'MESSAGE',
    '上传文件': 'UPLOAD',
    'UPLOAD': 'UPLOAD',
    '导航': 'NAVIGATE',
    'NAVIGATE': 'NAVIGATE'
}

common_keywords = {
    '执行': 'EXECUTE',
    'EXECUTE': 'EXECUTE',
    'SQL': 'SQL'
}

http_keywords = {
    'GET': 'GET',
    'POST': 'POST',
    'PUT': 'PUT',
    'PATCH': 'PATCH',
    'DELETE': 'DELETE',
    'OPTIONS': 'OPTIONS'
}

mobile_keywords = {
    '检查': 'CHECK',
    'CHECK': 'CHECK',
    '#检查': 'NOTCHECK',
    '#CHECK': 'NOTCHECK',
    '输入': 'INPUT',
    'INPUT': 'INPUT',
    '填写': 'SET_VALUE',
    'SET_VALUE': 'SET_VALUE',
    '点击': 'CLICK',
    'CLICK': 'CLICK',
    '轻点': 'TAP',
    'TAP': 'TAP',
    '按键码': 'PRESS_KEYCODE',  # Android 特有，常见代码 HOME:3, 菜单键：82，返回键：4
    'PRESS_KEYCODE': 'PRESS_KEYCODE',
    '滑动': 'SWIPE',
    'SWIPE': 'SWIPE',
    '划线': 'LINE',
    'LINE': 'LINE',
    '划线解锁': 'LINE_UNLOCK',
    'LINE_UNLOCK': 'LINE_UNLOCK',
    '摇杆': 'ROCKER',
    'ROCKER': 'ROCKER',
    '滚动': 'SCROLL',  # iOS 专用
    'SCROLL': 'SCROLL',
    '拖拽': 'DRAG_AND_DROP',
    'DRAG_AND_DROP': 'DRAG_AND_DROP',
    '摇晃': 'SHAKE',  # 貌似 Android 上不可用
    'SHAKE': 'SHAKE',
    '快速滑动': 'FLICK',
    'FLICK': 'FLICK',
    '滑动元素': 'FLICK_ELEMENT',
    'FLICK_ELEMENT': 'FLICK_ELEMENT',
    '长按': 'LONG_PRESS',
    'LONG_PRESS': 'LONG_PRESS',
    '缩小': 'PINCH',
    'PINCH': 'PINCH',
    '放大': 'ZOOM',
    'ZOOM': 'ZOOM',
    '隐藏键盘': 'HIDE_KEYBOARD',  # iOS 专用
    'HIDE_KEYBOARD': 'HIDE_KEYBOARD',
    '命名标签页': 'TAB_NAME',
    'TAB_NAME': 'TAB_NAME'
}

all_keywords = {}
for keywords in (web_keywords, common_keywords, http_keywords, mobile_keywords):
    all_keywords = dict(all_keywords, **keywords)

# 文件名后缀
_testcase = 'TestCase'  # '测试用例'
_elements = 'Elements'  # '页面元素表'
_report = 'Report'  # '测试结果'

# 特殊符号的转换别名
comma_lower = '#$%^&'
comma_upper = '&^%$#'
equals = '%^$#&'
vertical = '&$&*^&A@'

# header = ['用例编号', '用例标题', '前置条件', '测试步骤', '操作', '页面', '元素',
#'测试数据', '预期结果', '输出数据', '优先级', '设计者', '自动化标记', '测试结果', '备注']

header = {
    '用例编号': 'id',
    '用例标题': 'title',
    '前置条件': 'condition',
    '测试步骤': 'step',
    '操作': 'keyword',
    '页面': 'page',
    '元素': 'element',
    '测试数据': 'data',
    '预期结果': 'expected',
    '输出数据': 'output',
    '优先级': 'priority',
    '设计者': 'designer',
    '自动化标记': 'flag',
    '步骤结果': 'score',
    '用例结果': 'result',
    '备注': 'remark'
}

element_wait_timeout = 5  # 等待元素出现超时时间，单位：秒
page_flash_timeout = 90  # 页面刷新超时时间，单位：秒
