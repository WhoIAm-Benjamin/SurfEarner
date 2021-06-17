import re
import pyAesCrypt
from threading import Thread as Th
from os import system as execute
from os import (path,
                getcwd,
                remove)
from sys import argv
from sys import exit as ex
from time import sleep, time

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


# Получение логина и пароля из конфигурационого файла
def decryptor():
    file = 'settings.txt.crp'
    password_file = 'filepasswdroot'
    buffer_size = 512 * 1024
    pyAesCrypt.decryptFile(file, str(path.splitext(file)[0]), password_file, buffer_size)
    with open('settings.txt', 'r') as f:
        login, password, timeout = f.readlines()
    LOGIN = login.split(':')[1].strip('\n')
    PASSWORD = password.split(':')[1].strip('\n')
    TIMEOUT = timeout.split(':')[1].strip('\n')
    remove('settings.txt')
    return LOGIN, PASSWORD, TIMEOUT

def killer():
    while True:
        sleep(1200)
        execute('taskkill /f /IM chrome.exe')
        execute('taskkill /f /IM chromedriver.exe')

def wait_loading():
    # wait page loading
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'html'))
    )


def check_exist(operator, value):
    # check object exist
    global driver

    actions_to_operator = {
        'class_name': driver.find_element_by_class_name,
        'id': driver.find_element_by_id,
        'name': driver.find_element_by_name,
        'xpath': driver.find_element_by_xpath
    }

    if not operator in actions_to_operator:
        assert '[WARNING] Not such operator'
    is_exist = False
    try:
        actions_to_operator[operator](value)
        is_exist = True
    except:
        pass

    return is_exist


def wait(operator, value, interval=0.1):
    # wait while object not exist
    start = time()
    while not check_exist(operator, value):
        if time() - start > TIMEOUT:
            raise TimeoutError('Too long waiting for element')
        sleep(interval)


def get_path(file):
    return path.join(getcwd(), file)



def init_driver():
    """ Создание драйвера selenium для chrome
    :return: None
    """

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


def auth():
    """ Переход на сайт и авторизация
    :return: None
    """
    LOGIN, PASSWORD, TIMEOUT = decryptor()
    # если открыта вторая вкладка, то закрываем
    # необходимо при первом запуске программы
    if len(driver.window_handles) == 2:
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    driver.get('https://surfearner.com/#login')

    wait_loading()
    sleep(1)
    # если уже авторизованы ничего не делаем
    if driver.current_url == 'https://surfearner.com/partner':
        return
    elif driver.current_url == 'https://surfearner.com/client':
        driver.get('https://surfearner.com/partner')
        wait_loading()
        sleep(1)
        return

    # вводим данные пользователя
    driver.find_element_by_name('LoginForm[email]').send_keys(LOGIN)
    driver.find_element_by_name('LoginForm[password]').send_keys(PASSWORD)
    # если есть каптча, ждем ее решения
    if check_exist('name', 'secaptcha_val'):
        wait('class_name', 'solved')

    # нажимаем кнопку входа
    for btn in driver.find_elements_by_class_name('btn'):
        if btn.get_attribute('value') == 'Войти':
            btn.click()


def complate_tasks():
    """ Просмотр видео
    :return: None
    """
    def _remove_emoji(string):
        """ Удаляем эмоджи из строки для поиска на youtube
        :param string: string for compare
        :return: None
        """
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"
                                   u"\U0001F300-\U0001F5FF"
                                   u"\U0001F680-\U0001F6FF"
                                   u"\U0001F1E0-\U0001F1FF"
                                   u"\U00002702-\U000027B0"
                                   u"\U000024C2-\U0001F251"
                                   "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', string)

    # закрываем лишние вкладки
    while len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        return

    # ищем задания по просмотру видео
    wait('id', 'cpa-items')
    items = driver.find_element_by_id(
        'cpa-items'
    ).find_elements_by_class_name('item')
    try:
        relative_item = [i for i in items if 'YouTube' in i.text][0]
    except IndexError:
        relative_item = 0
    # если нет заданий, ждем 30 сек и обновляем страницу
    if not relative_item:
        sleep(30)
        # driver.refresh()
        return

    # минимальное время просмотра
    min_interval = int(re.findall(r'/ \d+', relative_item.text)[0][2:])
    try:
        driver.find_element_by_id('_se_visit_timer')
        raise WebDriverException
    except NoSuchElementException:
        pass
    if check_exist('class_name', 'btn blue'):
        return
    # узнаем, нужно ли переходить на youtube канал
    redircting = 'Переход' in relative_item.text
    # переходим по ссылке
    ActionChains(driver).move_to_element(
        relative_item.find_element_by_class_name('title')
    ).perform()
    relative_item.find_element_by_class_name('title').click()

    wait_loading()
    sleep(1)
    # если необходим переход на канал
    if redircting:
        # открываем канал
        sleep(3)
        wait('class_name', 'install_ext')
        btn = driver.find_element_by_class_name(
            'install_ext'
        ).find_element_by_class_name('btn')
        ActionChains(driver).move_to_element(btn).perform()
        sleep(1)
        ActionChains(driver).click().perform()

        # получаем название ролика
        wait('class_name', 'video_preview_text')
        video_name = driver.find_element_by_class_name(
            'video_preview_text'
        ).find_element_by_class_name('title').text
        video_name = _remove_emoji(video_name)

        sleep(2)
        wait('id', 'cpa_steps')
        btn = driver.find_element_by_id(
            'cpa_steps'
        ).find_element_by_class_name('btn')
        # дожидаемся открытия
        while len(driver.window_handles) != 2:
            ActionChains(driver).move_to_element(btn).perform()
            ActionChains(driver).click().perform()
            sleep(1)
        driver.switch_to.window(driver.window_handles[1])

        # если открывается больше 5 секунд, закрываем
        start = time()
        while not 'youtube' in driver.current_url:
            if time() - start > 10:
                driver.close()
                return
        wait_loading()

        # вводим название в поиск
        wait('id', 'tabsContent')
        driver.find_element_by_id(
            'tabsContent'
        ).find_element_by_id('button').click()

        # открываем нужное видео
        search = driver.find_element_by_id(
            'labelAndInputContainer'
        ).find_element_by_name('query')
        search.send_keys(video_name)
        sleep(1)
        search.send_keys(Keys.ENTER)

        wait_loading()
        sleep(1)
        try:
            driver.find_elements_by_id('video-title')[0].click()
        except IndexError:
            driver.close()
            return
        except StaleElementReferenceException:
            driver.close()
            return
    else:
        driver.switch_to.window(driver.window_handles[1])
        wait('id', 'surfearner_ntf_wrap')

    # ждем минимальное время
    wait_loading()
    sleep(min_interval)
    # start = time()
    # если есть таймер, ждем его истечения
    # в случае ошибки закрываем через 2 минуты
    if check_exist('id', '_se_visit_timer'):
        start = time()
        while not check_exist('class_name', 'closed'):
            if time() - start > 120:
                # return -1
                return
            try:
                int(driver.find_element_by_id('_se_visit_timer').text)
            except:
                if time() - start > 10:
                    break
    sleep(4)

    if len(driver.window_handles) > 1:
        driver.close()
    else:
        pass


def take_gift():
    """ Забираем подарок
    :return: None
    """
    # открываем окно подарка
    while driver.current_url != 'https://surfearner.com/gift':
        driver.get('https://surfearner.com/gift')
    # driver.switch_to.window(driver.window_handles[1])
    wait_loading()
    sleep(6) # ждем полной загрузки

    # запускаем видео
    driver.switch_to.frame(
        driver.find_element_by_id('video')
    )
    driver.find_element_by_class_name(
        'ytp-large-play-button'
    ).click()
    driver.switch_to_default_content()

    # ждем истечения таймера
    try:
        timer = driver.find_element_by_id('videorollText').find_element_by_tag_name('span')
    except WebDriverException:
        return
    while 1:
        try:
            if timer.text == '0':
                print('\a\a\a\a')
                break
        except:
            print('\a\a\a\a')
            sleep(15)
            break



def main():
    start = time()
    try:
        th = Th(target = killer, args = ())
        init_driver()
        auth()
        # take_gift()
        while 1:
            # проверяем подарок каждые полчаса
            if time() - start > 1800:
                take_gift()
                start = time()
            driver.switch_to.window(driver.window_handles[0])
            driver.get('https://surfearner.com/cpa')
            # если вернуло -1, перезапускаем браузер
            if complate_tasks() == -1:
                break
        driver.quit()
        ex()
    except WebDriverException:
        print('\n\n\a\aRestart\a\a\n\n')
        try:
            driver.quit()
        except NameError:
            pass
        finally:
            ex(main())
    except TimeoutError:
        print('\n\n\aTimeout error\a\n\n')
        driver.quit()
        ex(main())
    except KeyboardInterrupt:
        driver.quit()
        sleep(3)



if __name__ == '__main__':
    main()
