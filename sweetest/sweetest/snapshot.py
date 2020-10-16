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


# 解决打开图片大于 20M 的限制
Image.MAX_IMAGE_PIXELS = None

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


def blank(src, boxs):
    white = Image.new('RGB',(5000, 5000), 'white')   
    im = Image.open(src)
    for box in boxs:
        w = white.crop(box)
        im.paste(w, box[:2])
    im.save(src)


def cut(src, target, box):
    im = Image.open(src)
    im = im.crop(box)
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
            if v in ('#screen_shot','#ScreenShot'):
                self.output['#screen_shot'] = k
                step['output'].pop(k)
                self.screen_flag = True
            if v == ('#element_shot', '#ElementShot'):
                self.output['#element_shot'] = k
                step['output'].pop(k)
                self.element_flag = True

        # 处理图片比较
        self.expected = {}
        for data in (step['data'], step['expected']):
            if '#screen_shot' in data:
                self.screen_flag = True
                p = Path(data['#screen_shot']).stem
                self.expected['#screen_name'] = '('+p.split('[')[1].split(']')[0]+')' if '[' in p else p
                if Path(data['#screen_shot']).is_file():
                                     
                    step['snapshot']['expected_screen'] = data.pop('#screen_shot')
                else:                  
                    step['snapshot']['expected_screen'] = str(self.expected_folder / data.pop('#screen_shot'))

            if '#element_shot' in data:
                self.element_flag = True
                p = Path(data['#element_shot']).stem
                self.expected['#element_name'] = '('+p.split('[')[1].split(']')[0]+')' if '[' in p else p
                if Path(data['#element_shot']).is_file():
                    step['snapshot']['expected_element'] = data.pop('#element_shot')
                else:
                    step['snapshot']['expected_element'] = str(self.expected_folder / data.pop('#element_shot'))

            if '#cut' in data:
                self.expected['#cut'] = data.pop('#cut')
            if '#blank' in data:
                self.expected['#blank'] = data.pop('#blank')

    def web_screen(self, step, element):
        # 截图
        screen_v = self.output.get('#screen_shot', '')
        element_v = self.output.get('#element_shot', '')

        if g.snapshot or self.screen_flag or self.element_flag:
            from selenium.webdriver.support import expected_conditions as EC
            if not EC.alert_is_present()(g.driver):
                if self.expected.get('#screen_name'):
                    screen_name = self.expected['#screen_name']
                elif screen_v:
                    screen_name = screen_v
                else:
                    screen_name = ''
                if screen_name:
                    file_name = self.label + now() + '#screen' + '[' + screen_name + ']' + '.png'
                else:
                    file_name = self.label + now() + '#screen' + '.png'                                        
                step['snapshot']['real_screen'] = str(
                    Path(self.snapshot_folder) / file_name)
                get_screenshot(step['snapshot']['real_screen'])
                if screen_v:
                    g.var[screen_v] = step['snapshot']['real_screen']

        if element_v:
            file_name = self.label + now() + '#element' + '[' + element_v + ']' + '.png'
            step['snapshot']['real_element'] = str(Path(self.snapshot_folder) / file_name)
            crop(element, step['snapshot']['real_screen'], step['snapshot']['real_element'])
            g.var[element_v] = step['snapshot']['real_element']

    def web_check(self, step, element):

        def deep(src):
            # 把不需要比较的部分贴白
            if self.expected.get('#blank'):
                blank(src, eval(self.expected.get('#blank')))
            # 裁剪需要比较的部分
            if self.expected.get('#cut'):
                cut(src, src, eval(self.expected.get('#cut')))

        if Path(step['snapshot'].get('expected_screen', '')).is_file():
            # 屏幕截图比较
            image1 = Image.open(step['snapshot']['expected_screen'])
            image2 = Image.open(step['snapshot']['real_screen'])
            deep(step['snapshot']['real_screen'])
            histogram1 = image1.histogram()
            histogram2 = image2.histogram()
            differ = math.sqrt(reduce(operator.add, list(
                map(lambda a, b: (a - b)**2, histogram1, histogram2))) / len(histogram1))
            diff = ImageChops.difference(image1.convert('RGB'), image2.convert('RGB'))
            if differ == 0.0:
                # 图片间没有任何不同
                logger.info('SnapShot: screen_shot is the same')
            else:
                file_name = self.label + now() + 'diff_screen' + '.png'
                step['snapshot']['diff_screen'] = str(
                    Path(self.snapshot_folder) / file_name)
                diff.save(step['snapshot']['diff_screen'])
                raise Exception('SnapShot: screen_shot is diff: %s' % differ)
        elif step['snapshot'].get('expected_screen'):
            get_screenshot(step['snapshot']['expected_screen'])
            deep(step['snapshot']['expected_screen'])

        if Path(step['snapshot'].get('expected_element', '')).is_file():
            file_name = self.label + now() + '#element' + '[' + self.expected['#element_name'] + ']' + '.png'
            step['snapshot']['real_element'] = str(Path(self.snapshot_folder) / file_name)
            crop(element, step['snapshot']['real_screen'], step['snapshot']['real_element'])
            deep(step['snapshot']['real_element'])

            # 屏幕截图比较
            image1 = Image.open(step['snapshot']['expected_element'])
            image2 = Image.open(step['snapshot']['real_element'])
            histogram1 = image1.histogram()
            histogram2 = image2.histogram()
            differ = math.sqrt(reduce(operator.add, list(
                map(lambda a, b: (a - b)**2, histogram1, histogram2))) / len(histogram1))
            diff = ImageChops.difference(image1.convert('RGB'), image2.convert('RGB'))
            if differ == 0.0:
                logger.info('SnapShot: element_shot is the same')
            else:
                file_name = self.label + now() + 'diff_element' + '.png'
                step['snapshot']['diff_element'] = str(
                    Path(self.snapshot_folder) / file_name)
                diff.save(step['snapshot']['diff_element'])
                raise Exception('SnapShot: element_shot is diff: %s' % differ)
        elif step['snapshot'].get('expected_element'):
            crop(element, step['snapshot']['real_screen'], step['snapshot']['expected_element'])
            deep(step['snapshot']['expected_element'])

    def web_shot(self, step, element):
        self.web_screen(step, element)
        self.web_check(step, element)


    def windwos_capture(self, dialog, step):
        # 截图
        screen_v = self.output.get('#screen_shot', '')
        element_v = self.output.get('#element_shot', '')

        if g.snapshot or self.screen_flag:
            if self.expected.get('#screen_name'):
                screen_name = self.expected['#screen_name']
            elif screen_v:
                screen_name = screen_v
            else:
                screen_name = ''
            if screen_name:
                file_name = self.label + now() + '#screen' + '[' + screen_name + ']' + '.png'
            else:
                file_name = self.label + now() + '#screen' + '.png'               
            step['snapshot']['real_screen'] = str(Path(self.snapshot_folder) / file_name)
            pic = dialog.capture_as_image()
            pic.save(step['snapshot']['real_screen'])	
            if screen_v:
                g.var[screen_v] = step['snapshot']['real_screen']

        if element_v:
            file_name = self.label + now() + '#element' + '[' + element_v + ']' + '.png'
            step['snapshot']['real_element'] = str(Path(self.snapshot_folder) / file_name)

            element = step['element']
            if dialog.backend.name == 'win32':
                pic = dialog.window(best_match=element).capture_as_image()
            elif dialog.backend.name == 'uia':
                pic = dialog.child_window(best_match=element).capture_as_image()       
            pic.save(step['snapshot']['real_screen'])	            
            g.var[element_v] = step['snapshot']['real_element']


    def windwos_check(self, dialog, step):
        element = step['element']        
        if Path(step['snapshot'].get('expected_screen', '')).is_file():
            # 屏幕截图比较
            image1 = Image.open(step['snapshot']['expected_screen'])
            image2 = Image.open(step['snapshot']['real_screen'])
            histogram1 = image1.histogram()
            histogram2 = image2.histogram()
            differ = math.sqrt(reduce(operator.add, list(
                map(lambda a, b: (a - b)**2, histogram1, histogram2))) / len(histogram1))
            diff = ImageChops.difference(image1.convert('RGB'), image2.convert('RGB'))
            if differ == 0.0:
                # 图片间没有任何不同
                logger.info('SnapShot: screen_shot is the same')
            else:
                file_name = self.label + now() + 'diff_screen' + '.png'
                step['snapshot']['diff_screen'] = str(
                    Path(self.snapshot_folder) / file_name)
                diff.save(step['snapshot']['diff_screen'])
                raise Exception('SnapShot: screen_shot is diff: %s' % differ)
        elif step['snapshot'].get('expected_screen'):
            pic = dialog.capture_as_image()
            pic.save(step['snapshot']['expected_screen'])	            

        if Path(step['snapshot'].get('expected_element', '')).is_file():
            file_name = self.label + now() + '#element' + '.png'
            step['snapshot']['real_element'] = str(Path(self.snapshot_folder) / file_name)
            if dialog.backend.name == 'win32':
                pic = dialog.window(best_match=element).capture_as_image()
            elif dialog.backend.name == 'uia':
                pic = dialog.child_window(best_match=element).capture_as_image() 
            pic.save(step['snapshot']['real_element'])	            

            # 屏幕截图比较
            image1 = Image.open(step['snapshot']['expected_element'])
            image2 = Image.open(step['snapshot']['real_element'])
            histogram1 = image1.histogram()
            histogram2 = image2.histogram()
            differ = math.sqrt(reduce(operator.add, list(
                map(lambda a, b: (a - b)**2, histogram1, histogram2))) / len(histogram1))
            diff = ImageChops.difference(image1.convert('RGB'), image2.convert('RGB'))
            if differ == 0.0:
                logger.info('SnapShot: element_shot is the same')
            else:
                file_name = self.label + now() + 'diff_element' + '.png'
                step['snapshot']['diff_element'] = str(
                    Path(self.snapshot_folder) / file_name)
                diff.save(step['snapshot']['diff_element'])
                raise Exception('SnapShot: element_shot is diff: %s' % differ)
        elif step['snapshot'].get('expected_element'):
            if dialog.backend.name == 'win32':
                pic = dialog.window(best_match=element).capture_as_image()
            elif dialog.backend.name == 'uia':
                pic = dialog.child_window(best_match=element).capture_as_image()       
            pic.save(step['snapshot']['expected_element'])	            


    def windows_shot(self, dialog, step):
        self.windwos_capture(dialog, step)
        self.windwos_check(dialog, step)