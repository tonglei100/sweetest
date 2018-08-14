from sweetest.utility import Excel, data2dict
from sweetest.log import logger


def elements_format(data):
    elements = {}
    page = ''
    custom = ''
    for d in data:
        if d['page'].strip():
            page = d['page']
            custom = ''
        else:
            d['page'] = page

        if d.get('custom', '').strip():
            custom = d['custom']
        else:
            d['custom'] = custom

        elements[d['page'] + '-' + d['element']] = d
    return elements


class Elements:
    def __init__(self):
        pass

    def env(self):
        pass

    def get_elements(self, elements_file):
        d = Excel(elements_file)
        self.elements = elements_format(data2dict(d.read('elements')))

    def have(self, page, element):
        ele = element.split('#')

        if len(ele) >= 2:
            _el = ele[0] + '#'
        else:
            _el = element
        # 如果有<>,则不判断了
        if '<' in _el:
            return '', '通用' + '-' + element
        # 在元素定位表中查询
        elem = page + '-' + _el
        if self.elements.get(elem, ''):
            return self.elements[elem]['custom'], page + '-' + element
        else:
            # 查不到就在通用里查,还是查不到就报错
            elem = '通用' + '-' + _el
            if self.elements.get(elem, ''):
                return self.elements[elem]['custom'], '通用' + '-' + element
            else:
                logger.warning('Page:%s element:%s is not exist' %
                               (page, element))
                return '', element

    def get(self, element, flag=False):
        ele = element.split('#')
        # #号后面的值，即用户输入的变量
        _v = []
        # 支持多个变量替代，但是顺序要对应
        if len(ele) >= 2:
            _el = ele[0] + '#'
            _v = ele[1:]
        else:
            _el = element
        el = self.elements.get(_el, '')
        if not el:
            if flag:
                return _el, ''
            return _el, element.split('#', 1)[-1]
        value = el['value']
        for v in _v:
            value = value.replace('#', v, 1)
        return el, value


e = Elements()
