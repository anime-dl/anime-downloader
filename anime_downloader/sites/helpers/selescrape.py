from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.remote_connection import LOGGER as serverLogger
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
import tempfile
import os
import logging
import click
import time
import json

serverLogger.setLevel(logging.ERROR)
logger = logging.getLogger(__name__)


def get_data_dir():
    '''
    Gets the folder directory selescrape will store data, 
    such as cookies or browser extensions and logs.
    '''
    APP_NAME = 'anime downloader'
    return os.path.join(click.get_app_dir(APP_NAME), 'data')


def open_config():
    from anime_downloader.config import Config
    return Config

data = open_config()


def get_browser_config():
    '''
    Decides what browser selescrape will use.
    '''
    os_browser = { #maps os to a browser
    'linux':'firefox',
    'darwin':'chrome',
    'win32':'chrome'
    }
    for a in os_browser:
        if platform.startswith(a):
            browser =  os_browser[a]
        else:
            browser = 'chrome'
    value = data['dl']['selescrape_browser']
    value = value.lower() if value else value
    if value in ['chrome', 'firefox']:
        browser = value
    return browser


def get_browser_executable():
    value = data['dl']['selescrape_browser_executable_path']
    executable_value = value.lower() if value else value
    return executable_value


def get_driver_binary():
    value = data['dl']['selescrape_driver_binary_path']
    binary_path = value.lower() if value else value
    return binary_path


def cache_request(**kwargs):
    """
    This function saves the response from a Selenium request in a json.
    It uses timestamps so that the rest of the code can know if the cache has expired or not.
    """

    file = os.path.join(tempfile.gettempdir(), 'selenium_cached_requests.json')
    if os.path.isfile(file):
        with open(file, 'r') as f:
            tmp_cache = json.loads(f.read())
    else:
        tmp_cache = {}
    tmp_cache[kwargs.get('url')] = {
        'data': kwargs.get('text'), 
        'expiry': time.time(),
        'method': kwargs.get('method'),
        'cookies': kwargs.get('cookies'),
        'user_agent': kwargs.get('user_agent')
        }

    with open(file, 'w') as f:
        json.dump(tmp_cache, f, indent=4)

def check_cache(url):
    """
    This function checks if the cache file exists,
    if it exists then it will read the file
    And it will verify if the cache is less than or equal to 1 hour ago
    If it is, it will return it as it is.
    If it isn't, it will delete the expired cache from the file and return None
    If the file doesn't exist at all it will return None
    """
    file = os.path.join(tempfile.gettempdir(), 'selenium_cached_requests.json')
    if os.path.isfile(file):
        with open(file, 'r') as f:
            data = json.loads(f.read())
        try:
            data[url]
        except KeyError:
            return None
        timestamp = data[url]['expiry']
        if (time.time() - timestamp <= 3600):
            return data[url]
        else:
            data.pop(url, None)
            with open(file, 'w') as f:
                json.dump(data, f, indent=4)
            return None
    else:
        return None


def driver_select():
    '''
    it configures what each browser should do 
    and gives the driver variable that is used 
    to perform any actions below this function.
    '''
    browser = get_browser_config()
    data_dir = get_data_dir()
    executable = get_browser_executable()
    driver_binary = get_driver_binary()
    binary = None if not driver_binary else driver_binary
    if browser == 'firefox':
        fireFox_Options = webdriver.FirefoxOptions()
        fireFox_Options.headless = True
        fireFox_Options.add_argument('--log fatal')
        if binary == None:  
            driver = webdriver.Firefox(options=fireFox_Options, service_log_path=os.path.devnull)
        else:
            try:
                driver = webdriver.Firefox(options=fireFox_Options, service_log_path=os.path.devnull)
            except:
                driver = webdriver.Firefox(executable_path=binary, options=fireFox_Options, service_log_path=os.path.devnull)
    elif browser == 'chrome':
        from selenium.webdriver.chrome.options import Options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        profile_path = os.path.join(data_dir, 'Selenium_chromium')
        log_path = os.path.join(data_dir, 'chromedriver.log')
        chrome_options.add_argument('--log-level=OFF')
        chrome_options.add_argument(f"--user-data-dir={profile_path}")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(f'user-agent={get_random_header()}')
        if binary == None:
            if executable == None:
                driver = webdriver.Chrome(options=chrome_options)
            else:
                from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
                cap = DesiredCapabilities.CHROME
                cap['binary_location'] = executable
                driver = webdriver.Chrome(desired_capabilities=cap, options=chrome_options)
        else:
            if executable == None:
                driver = webdriver.Chrome(options=chrome_options)
            else:
                from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
                cap = DesiredCapabilities.CHROME
                cap['binary_location'] = executable
                driver = webdriver.Chrome(executable_path=binary, desired_capabilities=cap, options=chrome_options, service_log_path=os.path.devnull)
    return driver


def cloudflare_wait(driver):
    '''
    It waits until cloudflare has gone away before doing any further actions.
    The way it works is by getting the title of the page 
    and as long as it is "Just a moment..." it will keep waiting.
    This part of the code won't make the code execute slower 
    if the target website has no Cloudflare redirection.
    At most it will sleep 1 second as a precaution. 
    Also, i have made it time out after 50 seconds, useful if the target website is not responsive 
    and to stop it from running infinitely.
    '''
    abort_after = 50
    start = time.time()

    title = driver.title  # title = "Just a moment..."
    while title == "Just a moment...":
        time.sleep(0.25)
        delta = time.time() - start
        if delta >= abort_after:
            logger.error(f'Timeout:\tCouldnt bypass cloudflare. \
            See the screenshot for more info:\t{get_data_dir()}/screenshot.png')
            break
        title = driver.title
        if not title == "Just a moment...":
            break
    time.sleep(1) # This is necessary to make sure everything has loaded fine.


def request(request_type, url, **kwargs): #Headers not yet supported , headers={}
    params = kwargs.get('params', {})
    url = url if not params else url + '?' + urlencode(params)

    if bool(check_cache(url)):
        cached_data = check_cache(url)
        text = cached_data['data']
        user_agent = cached_data['user_agent']
        request_type = cached_data['method']
        cookies = cached_data['cookies']
        return SeleResponse(url, request_type, text, cookies, user_agent)

    else:
        
        driver = driver_select()
        driver.get(url)

        try:
            cloudflare_wait(driver)
            user_agent = driver.execute_script("return navigator.userAgent;") #dirty, but allows for all sorts of things above
            cookies = driver.get_cookies()
            text = driver.page_source
            driver.close()
            seleResponse = SeleResponse(url, request_type, text, cookies, user_agent)
            cache_request(**seleResponse.__dict__)
            return seleResponse

        except:
            driver.save_screenshot(f"{get_data_dir()}/screenshot.png");
            driver.close()
            logger.error(f'There was a problem getting the page: {url}. \
            See the screenshot for more info:\t{get_data_dir()}/screenshot.png')
            exit()



class SeleResponse:
    """
    Class for the selenium response.

    Attributes
    ----------
    url: string
        URL of the webpage.
    medthod: GET or POST
        Request type.
    text/content: string
        Webpage contents.
    cookies: dict
        Stored cookies from the website.
    user_agent: string
        User agent used on the webpage
    """
    def __init__(self, url, method, text, cookies, user_agent):
        self.url = url
        self.method = method
        self.text = text
        self.content = text
        self.cookies = cookies
        self.user_agent = user_agent

    def __str__(self):
        return self.text

    def __repr__(self):
        return '<SeleResponse URL: {} METHOD: {} TEXT: {} COOKIES {} USERAGENT {}>'.format(
            self.url, self.method, self.text, self.cookies, self.user_agent)
