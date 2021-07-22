from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sweet import log
from sweet.config import element_wait_timeout


def locating(driver, app, element, action=''):
    location = None
    try:
        el= element
        value = el['value']
    except:
        log.exception(f'locating the element:{element} is failure, this element is not define')
        raise Exception(f'locating the element:{element} is failure, this element is not define')

    if not isinstance(el, dict):
        raise Exception(f'locating the element:{element} is failure, this element is not define')

    wait = WebDriverWait(driver, element_wait_timeout)

    if el['by'].lower() in ('title', 'url', 'current_url'):
        return None
    else:
        try:
            location = wait.until(EC.presence_of_element_located(
                (getattr(By, el['by'].upper()), value)))
        except:
            sleep(5)
            try:
                location = wait.until(EC.presence_of_element_located(
                    (getattr(By, el['by'].upper()), value)))            
            except :
                raise Exception(f'locating the element:{element} is failure: timeout')                
    try:
        if driver.name in ('chrome', 'safari'):
            driver.execute_script(
                "arguments[0].scrollIntoViewIfNeeded(true)", location)
        else:
            driver.execute_script(
                "arguments[0].scrollIntoView(false)", location)
    except:
        pass

    try:
        if action == 'CLICK':
            location = wait.until(EC.element_to_be_clickable(
                (getattr(By, el['by'].upper()), value)))
        else:
            location = wait.until(EC.visibility_of_element_located(
                (getattr(By, el['by'].upper()), value)))
    except:
        pass

    return location


def locatings(elements):
    locations = {}
    for el in elements:
        locations[el] = locating(el)
    return locations


# def locating_data(keys):
#     data_location = {}
#     for key in keys:
#         data_location[key] = locating(key)
#     return data_location
