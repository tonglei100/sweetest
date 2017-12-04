from selenium import webdriver
from sweetest.exception import Error
from sweetest.config import element_wait_imeout, page_flash_timeout



class Global:
    def __init__(self):
        self.start_time = ''

    def set_driver(self, platform, app):
        self.var = {}
        self.snippet = {}

        if platform.lower() == 'pc':
            if app.lower() == 'ie':
                self.driver = webdriver.Ie()
            elif app.lower() == 'firefox':
                self.driver = webdriver.Firefox()
            elif app.lower() == 'chrome':
                options = webdriver.ChromeOptions()
                options.add_argument("--start-maximized")
                prefs = {"": ""}
                prefs["credentials_enable_service"] = False
                prefs["profile.password_manager_enabled"] = False
                options.add_experimental_option("prefs", prefs)
                options.add_argument('disable-infobars')
                options.add_experimental_option(
                    "excludeSwitches", ["ignore-certificate-errors"])
                self.driver = webdriver.Chrome(chrome_options=options)
            else:
                raise Error(
                    'Error: this browser is not supported or mistake name：%s' % browser)
            #等待元素超时时间
            self.driver.implicitly_wait(element_wait_imeout)  # seconds
            #页面刷新超时时间
            self.driver.set_page_load_timeout(page_flash_timeout) #seconds

        if platform.lower() == 'ios':
            print('Come soon...')

        if platform.lower() == 'android':
            print('Come soon...')

    def close(self):
        self.driver.close()


g = Global()
