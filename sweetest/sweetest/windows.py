from sweetest.globals import g
from sweetest.log import logger


class Windows:
    def __init__(self):
        self.init()

    def init(self):
        # 当前窗口名字，如：'新版门户首页窗口', 'HOME'
        self.current_window = ''
        # 所有窗口名字--窗口handle映射表，如:
        # {'新版门户首页窗口': 'CDwindow-3a12c86f-1986-4c02-ba7b-5a0ed94c5963', 'HOME': 'CDwindow-a3f0c44c-d269-4ff0-af38-c31ad70c69e3'}
        self.windows = {}
        # 当前frame名字
        self.frame = 0
        # 所有页面--窗口名字映射表，如：{'门户首页': '新版门户首页窗口'}
        self.pages = {}
        # 新开窗口标志
        self.new_window_flag = True
        # App context
        self.current_context = 'NATIVE_APP'

    def switch_window(self, page):
        if self.new_window_flag:
            if page in list(self.pages):
                page = '通用'
                g.current_page = '通用'
            self.new_window_flag = False

        if page != '通用':
            if page not in list(self.pages):
                # 如果当前页未注册，则需要先清除和当前窗口绑定的页面
                for k in list(self.pages):
                    if self.current_window == self.pages[k]:
                        self.pages.pop(k)
                # 在把当前窗口捆定到当前页面
                self.pages[page] = self.current_window

            elif self.pages[page] != self.current_window:
                # 如果当前窗口为 HOME，则关闭之
                if self.current_window == 'HOME':
                    g.driver.close()
                    self.windows.pop('HOME')
                # 再切换到需要操作的窗口
                tw = self.windows[self.pages[page]]
                logger.info('--- Switch Windows: %s' % repr(tw))
                g.driver.switch_to_window(tw)
                self.current_window = self.pages[page]
                logger.info('--- Current Windows: %s' % repr(self.current_window))

    def switch_frame(self, frame):
        if frame.strip():
            frame = [x.strip() for x in frame.split('|')]
            if frame != self.frame:
                if self.frame != 0:
                    g.driver.switch_to.default_content()
                for f in frame:
                    logger.info('--- Frame Value:  %s' % repr(f))
                    if f.startswith('#'):
                        f = int(f[1:])
                    elif '#' in f:
                        from sweetest.testcase import elements_format
                        from sweetest.locator import locating_element
                        element = elements_format('通用',f)[2]
                        f = locating_element(element)
                    logger.info('--- Switch Frame: %s' % repr(f))
                    g.driver.switch_to.frame(f)
                self.frame = frame
        else:
            if self.frame != 0:
                g.driver.switch_to.default_content()
                self.frame = 0

    def open(self, step):
        # 查看当前窗口是否已经注册到 windows 映射表
        c = self.windows.get(self.current_window, '')
        # 如果已经存在，则需要清除和当前窗口绑定的页面
        if c:
            for k in list(self.pages):
                if self.current_window == self.pages[k]:
                    self.pages.pop(k)
            # 并从映射表里剔除
            self.windows.pop(self.current_window)

        # 获取当前窗口handle
        handle = g.driver.current_window_handle
        # 注册窗口名称和handle
        self.register(step, handle)

    def register(self, step, handle):
        # 如果有提供新窗口名字，则使用该名字，否则使用默认名字：HOME
        #new_window = step['data'].get('新窗口', 'HOME')
        # 新窗口 变为 标签页名，兼容原有格式
        new_window = 'HOME'
        for k in ('新窗口', '标签页名', 'tabname'):
            if step['data'].get(k):
                new_window = step['data'].get(k)
        # 已存在同名的窗口，则
        if new_window in self.windows:
            # 1. 清除和当前窗口同名的旧窗口绑定的页面
            for k in list(self.pages):
                if new_window == self.pages[k]:
                    self.pages.pop(k)

            # 2. 切换到同名旧窗口去关闭它
            g.driver.switch_to_window(self.windows[new_window])
            g.driver.close()
            # 3. 并从窗口资源池 g.windows 里剔除
            self.windows.pop(new_window)
        # 然后切回当前窗口
        g.driver.switch_to_window(handle)
        # 再添加到窗口资源池 g.windows
        self.windows[new_window] = handle
        # 把当前窗口名字改为新窗口名称
        self.current_window = new_window
        # 新窗口标志置为是
        self.new_window_flag = True

    def close(self):
        all_handles = g.driver.window_handles
        for handle in all_handles:
            # 切换到每一个窗口,并关闭它
            g.driver.switch_to_window(handle)
            g.driver.close()
            logger.info('--- Close th Windows: %s' % repr(handle))

    def switch_context(self, context):
        if context.strip() == '':
            context = 'NATIVE_APP'
        logger.info('--- ALL   Contexts:%s' % g.driver.contexts)
        logger.info('--- Input  Context:%s' % repr(context))
        if context != self.current_context:
            if context == '':
                context = None
            logger.info('--- Switch Context:%s' % repr(context))
            g.driver.switch_to.context(context)
            self.current_context = context


w = Windows()
