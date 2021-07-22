from sweet import log


class Windows:

    def __init__(self):
        self.current_window = ''
        self.windows = {}
        self.frame = 0

    def tab(self, name):
        current_handle = self.driver.current_window_handle
        if name in self.windows:
            if current_handle != self.windows[name]:
                self.driver.switch_to_window(self.windows[name])
                log.debug(f'switch the windows: #tab:{name}, handle:{repr(self.windows[name])}')
            else:
                log.debug(f'current windows: #tab:{name}, handle:{repr(self.windows[name])}')
            
        else:
            all_handles = self.driver.window_handles
            for handle in all_handles:
                if handle not in self.windows.values():
                    self.windows[name] = handle
                    if handle != current_handle:
                        self.driver.switch_to_window(handle)
                        log.debug(f'switch the windows: #tab:{name}, handle:{repr(handle)}')
                    else:
                        log.debug(f'current windows: #tab:{name}, handle:{repr(current_handle)}')

        self.clear()

    def clear(self):  # 关闭未命名的 windows
        current_handle = self.driver.current_window_handle
        current_name = ''
        for name in self.windows:
            if current_handle == self.windows[name]:
                current_name = name

        all_handles = self.driver.window_handles        
        for handle in all_handles:
            # 未命名的 handle
            if handle not in self.windows.values():                 
                # 切换到每一个窗口,并关闭它
                self.driver.switch_to_window(handle)
                log.debug(f'switch the windows: #tab:<New>, handle:{repr(handle)}')
                self.driver.close()
                log.debug(f'close the windows: #tab:<New>, handle:{repr(handle)}')
                self.driver.switch_to_window(current_handle)
                log.debug(f'switch the windows: #tab:{current_name}, handle:{repr(current_handle)}')


    def switch(self):
        """
        docstring
        """
        current_handle = self.driver.current_window_handle
        use_handles = list(self.windows.values()) + [self.driver.current_window_handle]
        all_handles = self.driver.window_handles 
        for handle in all_handles:
            # 未命名的 handle
            if handle not in self.windows.values():                 
                # 切换到新窗口
                self.driver.switch_to_window(handle)
                log.debug(f'switch the windows: #tab:<New>, handle:{repr(handle)}')


    def switch_frame(self, frame):
        if frame.strip():
            frame = [x.strip() for x in frame.split('|')]
            if frame != self.frame:
                if self.frame != 0:
                    self.driver.switch_to.default_content()
                for f in frame:
                    log.debug(f'frame value: {repr(f)}')
                    if f.startswith('#'):
                        f = int(f[1:])
                    elif '#' in f:
                        from sweet.testcase import elements_format
                        from sweet.modules.web.locator import locating_element
                        element = elements_format('public', f)[2]
                        f = locating_element(element)
                    log.debug(f'    switch frame: {repr(f)}')
                    self.driver.switch_to.frame(f)
                self.frame = frame
        else:
            if self.frame != 0:
                self.driver.switch_to.default_content()
                self.frame = 0


    def close(self):
        all_handles = self.driver.window_handles
        for handle in all_handles:
            # 切换到每一个窗口,并关闭它
            self.driver.switch_to_window(handle)
            self.driver.close()
            log.debug(f'close th windows: {repr(handle)}')
