from pathlib import Path
from PIL import Image
from PIL import ImageChops
import math
import operator
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
                self.screen_flag = True

        # 处理图片比较
        self.expected = {}
        for data in (step['data'], step['expected']):
            if '#ScreenShot' in data:
                self.screen_flag = True
                if Path(data['#ScreenShot']).is_file():
                    self.expected['#ScreenShot'] = data['#ScreenShot']
                else:
                    self.expected['#ScreenShot'] = str(self.expected_folder / data.pop('#ScreenShot'))

            if '#ElementShot' in data:
                self.screen_flag = True
                if Path(data['#ElementShot']).is_file():
                    self.expected['#ElementShot'] = data['#ElementShot']
                else:
                    self.expected['#ElementShot'] = str(self.expected_folder / data.pop('#ElementShot'))

    def screen(self, step, element):
        # 截图
        screen_v = self.output.get('#ScreenShot', '')
        element_v = self.output.get('#ElementShot', '')

        if g.snapshot or self.screen_flag:
            from selenium.webdriver.support import expected_conditions as EC
            if not EC.alert_is_present()(g.driver):
                file_name = self.label + now() + '.png'
                step['ScreenShot'] = str(
                    Path(self.snapshot_folder) / file_name)
                g.driver.get_screenshot_as_file(step['ScreenShot'])
                if screen_v:
                    g.var[screen_v] = step['ScreenShot']

        if element_v:
            file_name = self.label + now() + '#Element' + '.png'
            step['ElementShot'] = str(Path(self.snapshot_folder) / file_name)
            crop(element, step['ScreenShot'], step['ElementShot'])
            g.var[element_v] = step['ElementShot']

    def check(self, step, element):
        if Path(self.expected.get('#ScreenShot', '')).is_file():
            # 屏幕截图比较
            image1 = Image.open(step['ScreenShot'])
            image2 = Image.open(step['ScreenShot'])
            histogram1 = image1.histogram()
            histogram2 = image2.histogram()
            differ = math.sqrt(reduce(operator.add, list(
                map(lambda a, b: (a - b)**2, histogram1, histogram2))) / len(histogram1))
            diff = ImageChops.difference(image1, image2)
            if differ == 0.0:
                # 图片间没有任何不同
                logger.info('SnapShot: ScreenShot is the same')
            else:
                file_name = '#' + self.label + now() + '.png'
                step['diffScreen'] = str(
                    Path(self.snapshot_folder) / file_name)
                diff.save(step['diffScreen'])
                raise Exception('SnapShot: ScreenShot is diff: %s' % differ)
        elif self.expected.get('ScreenShot'):
            g.driver.get_screenshot_as_file(self.expected['ScreenShot'])

        if Path(self.expected.get('#ElementShot', '')).is_file():
            file_name = self.label + now() + '#Element' + '.png'
            step['ElementShot'] = str(Path(self.snapshot_folder) / file_name)
            crop(element, step['ScreenShot'], step['ElementShot'])

            # 屏幕截图比较
            image1 = Image.open(self.expected['#ElementShot'])
            image2 = Image.open(step['ElementShot'])
            histogram1 = image1.histogram()
            histogram2 = image2.histogram()
            differ = math.sqrt(reduce(operator.add, list(
                map(lambda a, b: (a - b)**2, histogram1, histogram2))) / len(histogram1))
            diff = ImageChops.difference(image1, image2)
            if differ == 0.0:
                logger.info('SnapShot: ElementShot is the same')
            else:
                file_name = '#' + self.label + now() + '#Element' + '.png'
                step['diffElement'] = str(
                    Path(self.snapshot_folder) / file_name)
                diff.save(step['diffElement'])
                raise Exception('SnapShot: ElementShot is diff: %s' % differ)
        elif self.expected.get('#ElementShot'):
            crop(element, step['ScreenShot'], self.expected['#ElementShot'])

    def shot(self, step, element):
        self.screen(step, element)
        self.check(step, element)
