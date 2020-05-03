from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from anime_downloader.const import get_random_header
from selenium.webdriver.common.by import By
from urllib.parse import urlencode
from urllib.parse import urlsplit
from selenium import webdriver
from bs4 import BeautifulSoup
from logging import exception
from sys import platform
import requests, os
import click
import time
import json

header = get_random_header()
def test_os():
    if platform.startswith("linux"):
        os_name = "linux"
    elif platform == "darwin":
        os_name = "darwin"
    elif platform == "win32":
        os_name = "win32"
    return os_name
gg = test_os()
if gg.startswith("linux"):
    dd = '\\'
    aa = '/'
elif gg() == 'win32':
    dd = '/'
    aa = '\\'
else:
    raise exception('This OS is not currently supported.')
def get_config(): #can't use config because of circular import
    APP_NAME = 'anime downloader'
    directory = str(click.get_app_dir(APP_NAME) + aa + 'data').replace(dd, aa)
    return directory

def browsers():
    config = get_config()
    common_bs = ['chrome', 'firefox']
    if gg == "linux":
        common_bs = common_bs[0]
    elif gg == "darwin":
        print('Mac OS is not supported yet.')
    elif gg == "win32":
        common_bs = common_bs[0]
    return common_bs

def add_url_params(url, params):
    a = urlencode(params)
    b = url + '?' + a
    return b

default_browser = browsers()
def driver_select(name=default_browser):
    data_dir = get_config()
    if name == 'firefox' or name == 'ff' or name == 'f':
        fireFoxOptions = webdriver.FirefoxOptions()
        fireFoxOptions.headless = True
        fireFoxOptions.add_argument('--log fatal')
        fireFoxOptions.add_argument('-CreateProfile f"Selenium_firefox {data_dir}"')
        try:
            fireFoxOptions.add_argument(f'--install-app {data_dir}{aa}Extensions{aa}adblock.xpi')
        except:
            pass
        try:
            driver = webdriver.Firefox(firefox_options=fireFoxOptions)
        except:
            driver = webdriver.Firefox(firefox_options=fireFoxOptions, firefox_profile=f'{data_dir}{aa}Selenium_firefox', service_log_path=os.path.devnull)
    elif name == 'chrome' or name == 'chromium' or name == 'c':
        from selenium.webdriver.chrome.options import Options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        try:
            chrome_options.add_argument(f"load-extension={data_dir}{aa}Extensions{aa}ublock")
        except:
            pass
        chrome_options.add_argument(f'--log-path {data_dir}{aa}chromedriver.log')
        chrome_options.add_argument(f"--user-data-dir={data_dir}{aa}Selenium_chromium")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        user_agent = header
        chrome_options.add_argument(f'user-agent={user_agent}')
        driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver


def status_select(driver, url, status='hide'):
    try:
        if status == 'hide':
            driver.get(url)
        elif status == 'show':
            r = requests.head(url)
            if r.status_code == 503:
                raise exception("WARNING: This website's sevice is unavailable or has cloudflare on.")
            driver.get(url)
            return r.status_code
        else:
            driver.get(url)
    except requests.ConnectionError:
        raise exception("Failed to establish a connection.")
    

def cloudflare_wait(driver):
    try:
        title = driver.title  # title = "Just a moment..."
        while title == "Just a moment...":
            title = driver.title
            if not title == "Just a moment...":
                break
    except:
        pass
    time.sleep(1)

def request(request_type, url, headers={}, **kwargs): #Headers not yet supported
    params = {}
    for key, value in kwargs.items():
        if key == 'params':
            params = value

    new_url = add_url_params(url, params)
    driver = driver_select(default_browser)
    status = status_select(driver, new_url, 'hide')

    try:
        cloudflare_wait(driver)
        html = driver.page_source
        driver.close()
        return html
    except:
        driver.save_screenshot("screenshot.png");
        driver.close()

def get_by_css_selector(url, params, css, attr):
    new_url = add_url_params(url, params)
    driver = driver_select(default_browser)
    status = status_select(driver, new_url, 'hide')
    try:
        cloudflare_wait(driver)
        return WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css))).get_attribute(attr)
    except:
        driver.save_screenshot("screenshot.png");
        driver.close()

def get_by_xpath(url, params, full_xpath, attr, browser=default_browser):
    new_url = add_url_params(url, params)
    driver = driver_select(default_browser)
    status = status_select(driver, new_url, 'hide')
    try:
        cloudflare_wait(driver)
        return WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, full_xpath))).get_attribute(attr)
    except:
        driver.save_screenshot("screenshot.png");
        driver.close()
