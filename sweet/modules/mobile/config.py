

element_wait_timeout = 10  # 等待元素出现超时时间，单位：秒
page_flash_timeout = 90  # 页面刷新超时时间，单位：秒


keywords = {
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
    'TAB_NAME': 'TAB_NAME',
    '重启': 'LAUNCH_APP',
    'LAUNCH_APP': 'LAUNCH_APP',
    '锁屏状态': 'IS_LOCKED',
    'IS_LOCKED': 'IS_LOCKED',
    '锁屏': 'LOCK',
    'LOCK': 'LOCK',
    '解锁': 'UNLOCK',
    'UNLOCK': 'UNLOCK',         
}