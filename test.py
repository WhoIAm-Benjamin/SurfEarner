from shutil import copyfile
import os
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        NoSuchElementException,
                                        StaleElementReferenceException,
                                        WebDriverException)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

def get_path(file):
    return os.path.join(os.getcwd(), file)


chrome_options = webdriver.ChromeOptions()

chrome_options.add_argument(
    f'user-data-dir={get_path("ChromeData")}'
)
chrome_options.add_experimental_option('useAutomationExtension', False)
# загружаем расширение для surfearner
chrome_options.add_extension('extension.crx')

global driver
driver_path = 'chromedriver.exe'
driver = webdriver.Chrome(
    executable_path=driver_path,
    options=chrome_options,
)

# нужно для скрытия драйвера от сайтов
driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
    'source': """
          const newProto = navigator.__proto__
          delete newProto.webdriver
          navigator.__proto__ = newProto
          """
})
driver.execute_script(
    'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
)
driver.maximize_window()

input()

SHARE = open('settings.txt', 'r').read()

file_name = '1620736884.673145.png'
copyfile(
    os.path.join(os.getcwd(), f'Captcha\\{file_name}'),
    os.path.join(SHARE, 'captcha.png')
)

sleep(2)

# secaptcha-wrap
if os.path.exists(os.path.join(SHARE, 'result.txt')):
    value = open(os.path.join(SHARE, 'result.txt'), 'r').read()
    driver.switch_to.window(driver.window_handles[1])
    driver.switch_to.frame(
        driver.find_element_by_id('_se_visit_frame')
    )
    inputs = driver.find_element_by_id(
        'secaptcha-wrap'
    ).find_elements_by_tag_name('input')
    
    relative_input = [i for i in inputs if  i.get_attribute('value') == value][0]
    relative_input.click()









