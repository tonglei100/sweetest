from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sweetest.elements import e
from sweetest.globals import g
from sweetest.windows import w
from sweetest.log import logger
from sweetest.config import element_wait_timeout


def locating_element(element, action=''):
    el_location = None
    try:
        el, value = e.get(element)
    except:
        logger.exception(
            'Locating the element:%s is Failure, no element in define' % element)
        raise Exception('Locating the element:%s is Failure, no element in define' % element)

    wait = WebDriverWait(g.driver, element_wait_timeout)

    if el['by'].lower() in ('title', 'url', 'current_url'):
        return None
    elif action == 'CLICK':
        el_location = wait.until(EC.element_to_be_clickable(
            (getattr(By, el['by'].upper()), value)))
    else:
        el_location = wait.until(EC.presence_of_element_located(
            (getattr(By, el['by'].upper()), value)))

    try:
        if g.driver.name in ('chrome', 'safari'):
            g.driver.execute_script(
                "arguments[0].scrollIntoViewIfNeeded(true)", el_location)
        else:
            g.driver.execute_script(
                "arguments[0].scrollIntoView(false)", el_location)
    except:
        pass

    return el_location


def locating_elements(elements):
    elements_location = {}
    for el in elements:
        elements_location[el] = locating_element(el)
    return elements_location


def locating_data(keys):
    data_location = {}
    for key in keys:
        data_location[key] = locating_element(key)
    return data_location
