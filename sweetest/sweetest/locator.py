from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sweetest.elements import e
from sweetest.globals import g
from sweetest.exception import Error
from sweetest.log import logging
from sweetest.config import element_wait_timeout


def locating_element(element, action=''):
    el_location = None
    try:
        el, value = e.get(element)
    except Exception as exception:
        logging.warn(
            'Locating the element:%s is Failure, no element in define' % element)
        logging.debug(exception)
        raise Error(
            'Locating the element:%s is Failure, no element in define' % element)

    wait = WebDriverWait(g.driver, element_wait_timeout)

    if el['by'].lower() in ('title', 'url', 'current_url'):
        return None
    elif action == 'CLICK':
        el_location = wait.until(EC.element_to_be_clickable(
            (getattr(By, el['by'].upper()), value)))
    else:
        el_location = wait.until(EC.presence_of_element_located(
            (getattr(By, el['by'].upper()), value)))

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
