from pathlib import Path
from PIL import Image
from PIL import ImageChops
import math
import operator
import time
from functools import reduce
from sweetest.globals import g, now
from sweetest.log import logger
from sweetest.utility import mkdir


def crop(element, src, target):
    location = element.location
    size = element.size
    im = Image.open(src)
    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    im = im.crop((left, top, right, bottom))
    im.save(target)


def get_screenshot(file_path):
    if g.headless:
        width = g.driver.execute_script("return Math.max(document.body.scrollWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);")
        height = g.driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")
        g.driver.set_window_size(width,height)
        time.sleep(3)
    g.driver.get_screenshot_as_file(file_path)
    if g.headless:
        g.driver.set_window_size(1920,1080)


class Snapshot:
    def __init__(self):
        snapshot_plan = Path('snapshot') / g.plan_name
        self.snapshot_folder = snapshot_plan / g.start_time[1:]
        snapshot_expected = Path('snapshot') / 'expected'
        self.expected_folder = snapshot_expected / g.plan_name
        for p in (snapshot_plan, self.snapshot_folder, snapshot_expected, self.expected_folder):
            mkdir(p)

    def pre(self, step, label):
        self.label = label
        self.screen_flag = False
        self.element_flag = False
        # 处理输出数据中的截图设置
        self.output = {}
        for k, v in dict(step['output'].items()).items():
            if v == '#ScreenShot':
                self.output['#ScreenShot'] = k
                step['output'].pop(k)
                self.screen_flag = True
            if v == '#ElementShot':
                self.output['#ElementShot'] = k
                step['output'].pop(k)
                self.element_flag = True

        # 处理图片比较
        self.expected = {}
        for data in (step['data'], step['expected']):
            if '#ScreenShot' in data:
                self.screen_flag = True
                p = Path(data['#ScreenShot']).stem
                self.expected['#ScreenName'] = '('+p.split('[')[1].split(']')[0]+')' if '[' in p else p
                if Path(data['#ScreenShot']).is_file():
                                     
                    self.expected['#ScreenShot'] = data.pop('#ScreenShot')
                else:                  
                    self.expected['#ScreenShot'] = str(self.expected_folder / data.pop('#ScreenShot'))

            if '#ElementShot' in data:
                self.element_flag = True
                p = Path(data['#ElementShot']).stem
                self.expected['#ElementName'] = '('+p.split('[')[1].split(']')[0]+')' if '[' in p else p
                if Path(data['#ElementShot']).is_file():
                    self.expected['#ElementShot'] = data.pop('#ElementShot')
                else:
                    self.expected['#ElementShot'] = str(self.expected_folder / data.pop('#ElementShot'))

    def web_screen(self, step, element):
        # 截图
        screen_v = self.output.get('#ScreenShot', '')
        element_v = self.output.get('#ElementShot', '')

        if g.snapshot or self.screen_flag or self.element_flag:
            from selenium.webdriver.support import expected_conditions as EC
            if not EC.alert_is_present()(g.driver):
                if self.expected.get('#ScreenName'):
                    screen_name = self.expected['#ScreenName']
                elif screen_v:
                    screen_name = screen_v
                else:
                    screen_name = ''
                if screen_name:
                    file_name = self.label + now() + '#Screen' + '[' + screen_name + ']' + '.png'
                else:
                    file_name = self.label + now() + '#Screen' + '.png'                                        
                step['#ScreenShot'] = str(
                    Path(self.snapshot_folder) / file_name)
                get_screenshot(step['#ScreenShot'])
                if screen_v:
                    g.var[screen_v] = step['#ScreenShot']

        if element_v:
            file_name = self.label + now() + '#Element' + '[' + element_v + ']' + '.png'
            step['#ElementShot'] = str(Path(self.snapshot_folder) / file_name)
            crop(element, step['#ScreenShot'], step['#ElementShot'])
            g.var[element_v] = step['#ElementShot']

    def web_check(self, step, element):
        if Path(self.expected.get('#ScreenShot', '')).is_file():
            # 屏幕截图比较
            image1 = Image.open(self.expected['#ScreenShot'])
            image2 = Image.open(step['#ScreenShot'])
            histogram1 = image1.histogram()
            histogram2 = image2.histogram()
            differ = math.sqrt(reduce(operator.add, list(
                map(lambda a, b: (a - b)**2, histogram1, histogram2))) / len(histogram1))
            diff = ImageChops.difference(image1.convert('RGB'), image2.convert('RGB'))
            if differ == 0.0:
                # 图片间没有任何不同
                logger.info('SnapShot: ScreenShot is the same')
            else:
                file_name = '#' + self.label + now() + '.png'
                step['#diffScreen'] = str(
                    Path(self.snapshot_folder) / file_name)
                diff.save(step['#diffScreen'])
                raise Exception('SnapShot: ScreenShot is diff: %s' % differ)
        elif self.expected.get('#ScreenShot'):
            get_screenshot(self.expected['#ScreenShot'])

        if Path(self.expected.get('#ElementShot', '')).is_file():
            file_name = self.label + now() + '#Element' + '[' + self.expected['#ElementName'] + ']' + '.png'
            step['#ElementShot'] = str(Path(self.snapshot_folder) / file_name)
            crop(element, step['#ScreenShot'], step['#ElementShot'])

            # 屏幕截图比较
            image1 = Image.open(self.expected['#ElementShot'])
            image2 = Image.open(step['#ElementShot'])
            histogram1 = image1.histogram()
            histogram2 = image2.histogram()
            differ = math.sqrt(reduce(operator.add, list(
                map(lambda a, b: (a - b)**2, histogram1, histogram2))) / len(histogram1))
            diff = ImageChops.difference(image1.convert('RGB'), image2.convert('RGB'))
            if differ == 0.0:
                logger.info('SnapShot: ElementShot is the same')
            else:
                file_name = '#' + self.label + now() + '#Element' + '.png'
                step['#diffElement'] = str(
                    Path(self.snapshot_folder) / file_name)
                diff.save(step['#diffElement'])
                raise Exception('SnapShot: ElementShot is diff: %s' % differ)
        elif self.expected.get('#ElementShot'):
            crop(element, step['#ScreenShot'], self.expected['#ElementShot'])


    def web_shot(self, step, element):
        self.web_screen(step, element)
        self.web_check(step, element)


    def windwos_capture(self, dialog, step):
        # 截图
        screen_v = self.output.get('#ScreenShot', '')
        element_v = self.output.get('#ElementShot', '')

        if g.snapshot or self.screen_flag:
            if self.expected.get('#ScreenName'):
                screen_name = self.expected['#ScreenName']
            elif screen_v:
                screen_name = screen_v
            else:
                screen_name = ''
            if screen_name:
                file_name = self.label + now() + '#Screen' + '[' + screen_name + ']' + '.png'
            else:
                file_name = self.label + now() + '#Screen' + '.png'               
            step['#ScreenShot'] = str(Path(self.snapshot_folder) / file_name)
            pic = dialog.capture_as_image()
            pic.save(step['#ScreenShot'])	
            if screen_v:
                g.var[screen_v] = step['#ScreenShot']

        if element_v:
            file_name = self.label + now() + '#Element' + '[' + element_v + ']' + '.png'
            step['#ElementShot'] = str(Path(self.snapshot_folder) / file_name)

            element = step['element']
            if dialog.backend.name == 'win32':
                pic = dialog.window(best_match=element).capture_as_image()
            elif dialog.backend.name == 'uia':
                pic = dialog.child_window(best_match=element).capture_as_image()       
            pic.save(step['#ScreenShot'])	            
            g.var[element_v] = step['#ElementShot']


    def windwos_check(self, dialog, step):
        element = step['element']        
        if Path(self.expected.get('#ScreenShot', '')).is_file():
            # 屏幕截图比较
            image1 = Image.open(self.expected['#ScreenShot'])
            image2 = Image.open(step['#ScreenShot'])
            histogram1 = image1.histogram()
            histogram2 = image2.histogram()
            differ = math.sqrt(reduce(operator.add, list(
                map(lambda a, b: (a - b)**2, histogram1, histogram2))) / len(histogram1))
            diff = ImageChops.difference(image1.convert('RGB'), image2.convert('RGB'))
            if differ == 0.0:
                # 图片间没有任何不同
                logger.info('SnapShot: ScreenShot is the same')
            else:
                file_name = '#' + self.label + now() + '.png'
                step['#diffScreen'] = str(
                    Path(self.snapshot_folder) / file_name)
                diff.save(step['#diffScreen'])
                raise Exception('SnapShot: ScreenShot is diff: %s' % differ)
        elif self.expected.get('#ScreenShot'):
            pic = dialog.capture_as_image()
            pic.save(self.expected['#ScreenShot'])	            

        if Path(self.expected.get('#ElementShot', '')).is_file():
            file_name = self.label + now() + '#Element' + '.png'
            step['#ElementShot'] = str(Path(self.snapshot_folder) / file_name)
            if dialog.backend.name == 'win32':
                pic = dialog.window(best_match=element).capture_as_image()
            elif dialog.backend.name == 'uia':
                pic = dialog.child_window(best_match=element).capture_as_image() 
            pic.save(step['#ElementShot'])	            

            # 屏幕截图比较
            image1 = Image.open(self.expected['#ElementShot'])
            image2 = Image.open(step['#ElementShot'])
            histogram1 = image1.histogram()
            histogram2 = image2.histogram()
            differ = math.sqrt(reduce(operator.add, list(
                map(lambda a, b: (a - b)**2, histogram1, histogram2))) / len(histogram1))
            diff = ImageChops.difference(image1.convert('RGB'), image2.convert('RGB'))
            if differ == 0.0:
                logger.info('SnapShot: ElementShot is the same')
            else:
                file_name = '#' + self.label + now() + '#Element' + '.png'
                step['#diffElement'] = str(
                    Path(self.snapshot_folder) / file_name)
                diff.save(step['#diffElement'])
                raise Exception('SnapShot: ElementShot is diff: %s' % differ)
        elif self.expected.get('#ElementShot'):
            if dialog.backend.name == 'win32':
                pic = dialog.window(best_match=element).capture_as_image()
            elif dialog.backend.name == 'uia':
                pic = dialog.child_window(best_match=element).capture_as_image()       
            pic.save(self.expected['#ElementShot'])	            


    def windows_shot(self, dialog, step):
        self.windwos_capture(dialog, step)
        self.windwos_check(dialog, step)