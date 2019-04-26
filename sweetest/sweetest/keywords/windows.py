from pywinauto.application import Application
from pywinauto.keyboard import send_keys as sendkeys
from sweetest.globals import g


class Windows():
    def __init__(self, app):
        self.app = app
        self.backend = app.backend.name
        self.dialogs = []
        if self.backend == 'win32':
            self.func = 'window'
        else:
            self.func = 'child_window'

    def dialog(self, page):
        if page.startswith('>'):
            if self.dialogs:
                if self.backend == 'win32':
                    current_dialog = self.app.window(best_match=page[1:])
                elif self.backend == 'uia':
                    current_dialog = self.dialogs[-1].child_window(best_match=page[1:])
                self.dialogs.append(current_dialog)
                return current_dialog
            else:
                raise Exception('Dialog: your page start with ">", but there is no parent dialog')
        elif page.startswith('<'):
            if len(self.dialogs) >= 2:
                self.dialogs.pop()
                return self.dialogs[-1]
            else:
                raise Exception('Dialog: your page start with "<", but the parent is less than 1 dialog')
        elif page.strip() == '':
            if self.dialogs:
                return self.dialogs[-1]
            else:           
                raise Exception('Dialog: your page start with "", but there is no parent dialog') 
        else:
            current_dialog = self.app.window(best_match=page)
            self.dialogs = [current_dialog]
            return current_dialog            


def menu_select(dialog, step):
    element = step['element']
    if dialog.backend.name == 'win32':
        dialog.menu_select(element)
    elif dialog.backend.name == 'uia':
        for el in element.split('->'):
            dialog.child_window(best_match=el).select()


def select(dialog, step):
    element = step['element']
    getattr(dialog, g.windows.func)(best_match=element).select()


def click(dialog, step):
    element = step['element']
    getattr(dialog, g.windows.func)(best_match=element).click()

def input(dialog, step):
    element = step['element']
    vaule = step['data']['text']
    getattr(dialog, g.windows.func)(best_match=element).type_keys(vaule, with_spaces=True)


def set_text(dialog, step):
    element = step['element']
    vaule = step['data']['text']
    getattr(dialog, g.windows.func)(best_match=element).set_edit_text(vaule)


def send_keys(dialog, step):
    element = step['element']
    vaule = step['data'].get('text')
    dialog.set_focus()
    if element:
        getattr(dialog, g.windows.func)(best_match=element).set_focus()
        sendkeys(vaule)
    else:
        sendkeys(vaule)


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