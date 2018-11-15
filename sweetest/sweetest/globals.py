from selenium import webdriver
from sweetest.config import element_wait_timeout, page_flash_timeout


class Global:
    def __init__(self):
        self.start_time = ''
        self.project_name = ''
        self.sheet_name = ''

    def init(self, desired_caps, server_url):
        self.desired_caps = desired_caps
        self.server_url = server_url
        self.platform = desired_caps.get('platformName', '')
        self.browserName = desired_caps.get('browserName', '')
        self.var = {}
        self.snippet = {}
        self.current_page = '通用'
        self.db = {}
        self.http = {}
        self.baseurl = {}
        self.driver = ''
        self.action = {}

    def set_driver(self):
        if self.platform.lower() == 'desktop':
            if self.browserName.lower() == 'ie':
                self.driver = webdriver.Ie()
            elif self.browserName.lower() == 'firefox':
                self.driver = webdriver.Firefox()
                self.driver.maximize_window()
            elif self.browserName.lower() == 'chrome':
                options = webdriver.ChromeOptions()
                options.add_argument("--start-maximized")
                #指定浏览器分辨率，当"--start-maximized"无效时使用
                #options.add_argument('window-size=1920x1080')
                prefs = {"": ""}
                prefs["credentials_enable_service"] = False
                prefs["profile.password_manager_enabled"] = False
                options.add_experimental_option("prefs", prefs)
                options.add_argument('disable-infobars')
                options.add_experimental_option(
                    "excludeSwitches", ["ignore-certificate-errors"])
                self.driver = webdriver.Chrome(chrome_options=options)
            else:
                raise Exception(
                    'Error: this browser is not supported or mistake name：%s' % self.browserName)
            # 等待元素超时时间
            self.driver.implicitly_wait(element_wait_timeout)  # seconds
            # 页面刷新超时时间
            self.driver.set_page_load_timeout(page_flash_timeout)  # seconds

        if self.platform.lower() == 'ios':
            from appium import webdriver as appdriver
            self.driver = appdriver.Remote(self.server_url, self.desired_caps)

        if self.platform.lower() == 'android':
            from appium import webdriver as appdriver
            self.driver = appdriver.Remote(self.server_url, self.desired_caps)


g = Global()
