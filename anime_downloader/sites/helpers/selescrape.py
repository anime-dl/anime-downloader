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
import requests
import os
import click
import time
import json


def test_os(): #pretty self-explanatory
    if platform.startswith("lin"):
        os_name = "linux"
    elif platform.startswith("da"):
        os_name = "darwin"
    elif platform.startswith("win"):
        os_name = "win32"
    return os_name

def get_data_dir(): #gets the folder directory selescrape will store data, such as cookies or browser extensions and logs.
    APP_NAME = 'anime downloader'
    directory = os.path.join(click.get_app_dir(APP_NAME), 'data')
    print(directory)
    #
    #
def get_browser(): #pretty self-explanatory
    ostest = test_os()
    common_bs = ['chrome', 'firefox']
    if ostest.startswith("linux"):
        common_bs = common_bs[1]
    elif ostest == "darwin":
        common_bs = common_bs[0]
    elif ostest == "win32":
        common_bs = common_bs[0]
    return common_bs
#
#
def get_config(): #can't import config directly because of circular import
    try:
        APP_NAME = 'anime downloader'
        with open(os.path.join(click.get_app_dir(APP_NAME), 'config.json')) as json_file:
            data = json.load(json_file)
            browser_value = data['dl']['selescrape_browser'].lower()
            if browser_value == '.':
                browser = get_browser()
            elif browser_value == 'chrome' or browser_value == 'c':
                browser = browser_value
            elif browser_value == 'firefox' or browser_value == 'f':
                browser = browser_value
        return browser
    except:
        browser = get_browser()
#
#
def add_url_params(url, params): #pretty self-explanatory
    encoded_params = urlencode(params)
    url = url + '?' + encoded_params
    return url
#
#
def driver_select(): #it configures what each browser should do and gives the driver variable that is used to perform any actions below this def
    browser = get_config()
    data_dir = get_data_dir()
    if browser == 'firefox':
        fireFoxOptions = webdriver.FirefoxOptions()
        fireFoxOptions.headless = True
        fireFoxOptions.add_argument('--log fatal')
        fireFoxOptions.add_argument('-CreateProfile f"Selenium_firefox {data_dir}"')
        adblock = os.path.join(data_dir, 'Extensions', 'adblock.xpi')
        profile_path = os.path.join(data_dir, 'Selenium_firefox')
        try:
            fireFoxOptions.add_argument(f'--install-app {adblock}')
        except:
            pass
        try:
            driver = webdriver.Firefox(firefox_options=fireFoxOptions)
        except:
            driver = webdriver.Firefox(firefox_options=fireFoxOptions, firefox_profile=f'{profile_path}', service_log_path=os.path.devnull)


    elif browser == 'chrome':
        from selenium.webdriver.chrome.options import Options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        try:
            extension_path = os.path.join(data_dir, 'Extensions', 'adblock.crx')
            chrome_options.add_extension(extension_path)
        except:
            pass
        header = get_random_header()
        profile_path = os.path.join(data_dir, 'Selenium_chromium')
        log_path = os.path.join(data_dir, 'chromedriver.log')
        chrome_options.add_argument(f'--log-path {log_path}')
        chrome_options.add_argument(f"--user-data-dir={profile_path}")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        user_agent = header
        chrome_options.add_argument(f'user-agent={user_agent}')
        driver = webdriver.Chrome(options=chrome_options)
    return driver
#
#
def status_select(driver, url, status='hide'): #for now it doesnt do what its name suggests, i have planned to add a status reporter of the http response code.
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
#    
#
def cloudflare_wait(driver): #it waits until cloudflare has gone away before doing any further actions.
    try:
        title = driver.title  # title = "Just a moment..."
        while title == "Just a moment...": #or "another title for different kinds of Cloudflare protection."
            title = driver.title
            if not title == "Just a moment...":
                break
    except:
        pass
    time.sleep(1)
#
#
def request(url, params={}, request_type='lol', **kwargs): #Headers not yet supported , headers={}
    for key, value in kwargs.items():
        if key == 'params':
            params = value
    new_url = add_url_params(url, params)
    driver = driver_select()
    status = status_select(driver, new_url, 'hide')

    try:
        cloudflare_wait(driver)
        html = driver.page_source
        driver.close()
        return html
    except:
        driver.save_screenshot("screenshot.png");
        driver.close()
#
#
def get_by_css_selector(url, params, css, attr): #this is added as an optional command,
                                                    #it returns the attribute of a web element by the css selector 
    browser = get_config()
    new_url = add_url_params(url, params)
    driver = driver_select(browser)
    status = status_select(driver, new_url, 'hide')
    try:
        cloudflare_wait(driver)
        return WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css))).get_attribute(attr)
    except:
        driver.save_screenshot("screenshot.png");
        driver.close()
#
#
def get_by_xpath(url, params, full_xpath, attr):
    browser = get_config()
    new_url = add_url_params(url, params)
    driver = driver_select(browser)
    status = status_select(driver, new_url, 'hide')
    try:
        cloudflare_wait(driver)
        return WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, full_xpath))).get_attribute(attr)
    except:
        driver.save_screenshot("screenshot.png");
        driver.close()
#
#