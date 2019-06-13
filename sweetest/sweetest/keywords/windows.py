from pywinauto.application import Application
from pywinauto.keyboard import send_keys as sendkeys
import re
from sweetest.log import logger
from sweetest.globals import g
from sweetest.utility import compare

class Windows():
    def __init__(self, app):
        self.app = app
        self.backend = app.backend.name
        self.dialogs = []

    def dialog(self, page):
        if page == []:
            if self.dialogs:
                return self.dialogs[-1]
            else:           
                raise Exception('Dialog: your page start with "", but there is no parent dialog')
        elif  page[0] == '<':
            if len(self.dialogs) >= 2:
                self.dialogs.pop()
                return self.dialog(page[1:])
            else:
                raise Exception('Dialog: your page start with "<", but the parent is less than 1 dialog')            
        elif page[0] == '>':
            if self.dialogs:
                if self.backend == 'win32':
                    current_dialog = self.app.window(best_match=page[1])
                elif self.backend == 'uia':
                    current_dialog = self.dialogs[-1].child_window(best_match=page[1])
                self.dialogs.append(current_dialog)
                return self.dialog(page[2:])
            else:
                raise Exception('Dialog: your page start with ">", but there is no parent dialog')
        else:
            current_dialog = self.app.window(best_match=page[0])
            self.dialogs = [current_dialog]
            return self.dialog(page[1:])


def menu_select(dialog, step):
    element = step['element']
    try:
        dialog.menu_select(element)
    except:
        for el in element.split('->'):
            dialog.child_window(best_match=el).select()


def select(dialog, step):
    element = step['element']
    if dialog.backend.name == 'win32':
        dialog.window(best_match=element).select()
    elif dialog.backend.name == 'uia':
        dialog.child_window(best_match=element).select()


def click(dialog, step):
    element = step['element']
    if dialog.backend.name == 'win32':
        dialog.window(best_match=element).click_input()
    elif dialog.backend.name == 'uia':
        dialog.child_window(best_match=element).click_input()


def check_off(dialog, step):
    element = step['element']
    if dialog.backend.name == 'win32':
        dialog.window(best_match=element).check()
    elif dialog.backend.name == 'uia':
        dialog.child_window(best_match=element).check()


def double_click(dialog,step):
    element = step['element']
    if dialog.backend.name == 'win32':
        dialog.window(best_match=element).double_click_input()
    elif dialog.backend.name == 'uia':
        dialog.child_window(best_match=element).double_click_input()    


def input(dialog, step):
    element = step['element']
    vaule = step['data']['text']
    if dialog.backend.name == 'win32':
        dialog.window(best_match=element).type_keys(vaule, with_spaces=True, with_newlines='\r\n')
    elif dialog.backend.name == 'uia':
        dialog.child_window(best_match=element).type_keys(vaule, with_spaces=True, with_newlines='\r\n')


def set_text(dialog, step):
    element = step['element']
    vaule = step['data']['text']
    if dialog.backend.name == 'win32':
        dialog.window(best_match=element).set_edit_text(vaule)
    elif dialog.backend.name == 'uia':
        dialog.child_window(best_match=element).set_edit_text(vaule)


def send_keys(dialog, step):
    element = step['element']
    vaule = step['data'].get('text')
    dialog.set_focus()
    if element:
        if dialog.backend.name == 'win32':
            dialog.window(best_match=element).set_focus()
        elif dialog.backend.name == 'uia':
            dialog.child_window(best_match=element).set_focus()
        sendkeys(vaule)
    else:
        sendkeys(vaule)


def check(dialog, step):
    element = step['element']
    data = step['data']
    if not data:
        data = step['expected']
    output = step['output']
    for key in data:
        # 预期结果
        expected = data[key]
        # 切片操作处理
        s = re.findall(r'\[.*?\]', key)
        if s:
            s = s[0]
            key = key.replace(s, '')

        if key == 'text':
            if dialog.backend.name == 'win32':
                real = dialog.window(best_match=element).texts()[0].replace('\r\n', '\n')
            elif dialog.backend.name == 'uia':
                real = dialog.child_window(best_match=element).texts()[0].replace('\r\n', '\n')
        elif key == 'value':
            if dialog.backend.name == 'win32':
                real = dialog.window(best_match=element).text_block().replace('\r\n', '\n')
            elif dialog.backend.name == 'uia':
                real = dialog.child_window(best_match=element).get_value().replace('\r\n', '\n')                                         
        if s:
            real = eval('real' + s)

        if key == 'selected':
            if dialog.backend.name == 'win32':
                real = dialog.window(best_match=element).is_selected()
            elif dialog.backend.name == 'uia':
                real = dialog.child_window(best_match=element).is_selected()          
        elif key == 'checked':
            if dialog.backend.name == 'win32':
                real = dialog.window(best_match=element).is_checked()
            elif dialog.backend.name == 'uia':
                real = dialog.child_window(best_match=element).is_checked()
        elif key == 'enabled':
            if dialog.backend.name == 'win32':
                real = dialog.window(best_match=element).is_enabled()
            elif dialog.backend.name == 'uia':
                real = dialog.child_window(best_match=element).is_enabled()
        elif key == 'visible':
            if dialog.backend.name == 'win32':
                real = dialog.window(best_match=element).is_visible()
            elif dialog.backend.name == 'uia':
                real = dialog.child_window(best_match=element).is_visible()                
        elif key == 'focused':
            if dialog.backend.name == 'win32':
                real = dialog.window(best_match=element).is_focused()
            elif dialog.backend.name == 'uia':
                real = dialog.child_window(best_match=element).is_focused() 

        logger.info('DATA:%s' % repr(expected))
        logger.info('REAL:%s' % repr(real))
        compare(expected, real)

    # 获取元素其他属性
    for key in output:
        k = output[key]
        if dialog.window(best_match=element).class_name() == 'Edit' and k == 'text':
            k = 'value'
                        
        if k == 'text':
            if dialog.backend.name == 'win32':
                g.var[key] = dialog.window(best_match=element).texts()[0].replace('\r\n', '\n') 
            elif dialog.backend.name == 'uia':
                g.var[key] = dialog.child_window(best_match=element).texts()[0].replace('\r\n', '\n')

        if k == 'value':
            if dialog.backend.name == 'win32':
                g.var[key] = dialog.window(best_match=element).text_block().replace('\r\n', '\n') 
            elif dialog.backend.name == 'uia':
                g.var[key] = dialog.child_window(best_match=element).get_value().replace('\r\n', '\n')   


def window(dialog, step):
    element = step['element']
    if element.lower() in ('最小化', 'minimize'):
        dialog.minimize()
    elif element.lower() in ('最大化', 'maximize'):
        dialog.maximize()
    elif element.lower() in ('恢复', 'restore'):
        dialog.restore()          
    elif element.lower() in ('关闭', 'close'):
        dialog.close()
    elif element.lower() in ('前台', 'set_focus'):
        dialog.set_focus()
    elif element.lower() in ('重置', 'reset'):
        for i in range(10):
            if not dialog.has_focus():
                try:
                    # 如果弹出保存窗口
                    save = dialog.get_active()
                    element = '(N)'
                    if dialog.backend.name == 'win32':
                        save.window(best_match=element).click_input()
                    elif dialog.backend.name == 'uia':
                        save.child_window(best_match=element).click_input()                
                except:
                    pass
                #按 Alt+F4 关闭窗口
                sendkeys('%{F4}')
            else:
                break
        else:
            raise Exception(f'Reset the Windows is failure: try Alt+F4 for {i+1} times')