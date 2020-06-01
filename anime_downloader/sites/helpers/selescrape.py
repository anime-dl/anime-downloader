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


def get_data_dir():
    """
    gets the folder directory selescrape will store data, 
    such as cookies or browser extensions and logs.
    """
    APP_NAME = 'anime downloader'
    return os.path.join(click.get_app_dir(APP_NAME), 'data')


def open_config():
    try:
        APP_NAME = 'anime downloader'
        with open(os.path.join(click.get_app_dir(APP_NAME), 'config.json'), 'r') as json_file:
            data = json.load(json_file)
            json_file.close()
        return data
    except:
        return 'Error, file not formated correctly or does not exist'

    
data = open_config()


def get_browser_config():
    """
    decides what browser selescrape will use
    """
    if data == 'Error, file not formated correctly or does not exist':
        os_browser = { #maps os to a browser
        'linux':'firefox',
        'darwin':'chrome',
        'win32':'chrome'
        }
        for a in os_browser:
            if platform.startswith(a):
                browser =  os_browser[a]
            else:
                browser = 'firefox'
    else:
        value = data['dl']['selescrape_browser'].lower()
        if value in ['chrome', 'firefox']:
            browser = value
    return browser


def get_browser_executable():
    if data == 'Error, file not formated correctly or does not exist':
        executable_value = '.'
    else:
        executable_value = data['dl']['selescrape_browser_executable_path'].lower()
    return executable_value


def get_driver_binary():
    if data == 'Error, file not formated correctly or does not exist':
        binary_path = '.'
    else:
        binary_path = data['dl']['selescrape_driver_binary_path'].lower()
    return binary_path


def add_url_params(url, params): #pretty self-explanatory
    encoded_params = urlencode(params)
    url = url + '?' + encoded_params
    return url


def driver_select(): #
    """
    it configures what each browser should do 
    and gives the driver variable that is used 
    to perform any actions below this def
    """
    browser = get_browser_config()
    data_dir = get_data_dir()
    executable = get_browser_executable()
    driver_binary = get_driver_binary()
    if driver_binary == '.':
        binary = None
    else:
        binary = driver_binary
    if browser == 'firefox':
        fireFoxOptions = webdriver.FirefoxOptions()
        fireFoxOptions.headless = True
        fireFoxOptions.add_argument('--log fatal')
        fireFoxOptions.add_argument('-CreateProfile f"Selenium_firefox {data_dir}"')
        adblock = os.path.join(data_dir, 'Extensions', 'adblock.xpi')
        profile_path = os.path.join(data_dir, 'Selenium_firefox')
        if os.path.exists(profile_path):
            pass
        else:
            os.mkdir(profile_path)
        try:
            fireFoxOptions.add_argument(f'--install-app {adblock}')
        except:
            pass
        if driver_binary == '.':  
            try:
                driver = webdriver.Firefox(options=fireFoxOptions, service_log_path=os.path.devnull)
            except:
                driver = webdriver.Firefox(options=fireFoxOptions, firefox_profile=f'{profile_path}', service_log_path=os.path.devnull)
        else:
            try:
                driver = webdriver.Firefox(options=fireFoxOptions, service_log_path=os.path.devnull)
            except:
                driver = webdriver.Firefox(executable_path=driver_binary, options=fireFoxOptions, firefox_profile=f'{profile_path}', service_log_path=os.path.devnull)
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
        # header = get_random_header()
        profile_path = os.path.join(data_dir, 'Selenium_chromium')
        log_path = os.path.join(data_dir, 'chromedriver.log')
        chrome_options.add_argument(f'--log-path {log_path}')
        chrome_options.add_argument(f"--user-data-dir={profile_path}")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        # user_agent = header
        chrome_options.add_argument(f'user-agent={get_random_header()}')
        if driver_binary == '.':
            if executable == '.':
                driver = webdriver.Chrome(options=chrome_options)
            else:
                from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
                cap = DesiredCapabilities.CHROME
                cap['binary_location'] = executable
                driver = webdriver.Chrome(desired_capabilities=cap, options=chrome_options)
        else:
            if executable == '.':
                driver = webdriver.Chrome(options=chrome_options)
            else:
                from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
                cap = DesiredCapabilities.CHROME
                cap['binary_location'] = executable
                driver = webdriver.Chrome(executable_path=driver_binary, desired_capabilities=cap, options=chrome_options)
    return driver


def status_select(driver, url, status='hide'):
    """
    for now it doesnt do what its name suggests, 
    i have planned to add a status reporter of the http response code.
    """
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
        raise exception("Failed to establish a connection using the requests library.")

        
def cloudflare_wait(driver):
    """
    it waits until cloudflare has gone away before doing any further actions.
    """
    abort_after = 30
    start = time.time()

    title = driver.title  # title = "Just a moment..."
    while title == "Just a moment...":
        time.sleep(0.25)
        delta = time.time() - start
        if delta >= abort_after:
            raise Exception(f'Timeout:\nCouldnt bypass cloudflare. See the screenshot for more info:\n{get_data_dir()}/screenshot.png')
        title = driver.title
        if not title == "Just a moment...":
            break
    time.sleep(1)
    
    
def request(url, request_type='GET', **kwargs): #Headers not yet supported , headers={}, **kwargs
    params = {}
    for key, value in kwargs.items():
        if key == 'params':
            params = value
    nothing = request_type
    new_url = add_url_params(url, params)
    driver = driver_select()
    status = status_select(driver, new_url, 'hide')
    try:
        cloudflare_wait(driver)
        html = driver.page_source
        driver.close()
        return html
    except:
        driver.save_screenshot(f"{get_data_dir()}/screenshot.png");
        driver.close()
