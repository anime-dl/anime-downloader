from selenium.webdriver.remote.remote_connection import LOGGER as serverLogger
from anime_downloader.const import get_random_header
from urllib.parse import urlencode
from selenium import webdriver
from sys import platform
import tempfile
import logging
import click
import time
import json
import os


def open_config():
    from anime_downloader.config import Config
    return Config


cache = False
serverLogger.setLevel(logging.ERROR)
logger = logging.getLogger(__name__)
TEMP_FOLDER = os.path.join(tempfile.gettempdir(), 'AnimeDL-SeleniumCache')
data = open_config()

if not os.path.isdir(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)


def get_data_dir():
    '''
    Gets the folder directory selescrape will store data,
    such as cookies or browser extensions and logs.
    '''
    APP_NAME = 'anime downloader'
    return os.path.join(click.get_app_dir(APP_NAME), 'data')


def get_browser_config():
    '''
    Decides what browser selescrape will use.
    '''
    os_browser = {  # maps os to a browser
        'linux': 'firefox',
        'darwin': 'chrome',
        'win32': 'chrome'
    }
    for a in os_browser:
        if platform.startswith(a):
            browser = os_browser[a]
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
    if executable_value:
        return executable_value


def get_driver_binary():
    value = data['dl']['selescrape_driver_binary_path']
    if value:
        return value


def cache_request(sele_response):
    """
    This function saves the response from a Selenium request in a json.
    It uses timestamps to can know if the cache has expired or not.
    """
    if not cache:
        return

    file = os.path.join(TEMP_FOLDER, 'selenium_cached_requests.json')

    if os.path.isfile(file):
        with open(file, 'r') as f:
            tmp_cache = json.load(f)
    else:
        tmp_cache = {}

    data = sele_response.__dict__
    url = data['url']
    url = (url[:-1] if url and url[-1] == '/' else url)

    tmp_cache[url] = {
        'data': data['text'],
        'expiry': time.time(),
        'method': data['method'],
        'cookies': data['cookies'],
        'user_agent': data['user_agent']
    }

    with open(file, 'w') as f:
        json.dump(tmp_cache, f, indent=4)


def check_cache(url):
    """
    This function checks if the cache file exists,
    if it exists then it will read the file
    And it will verify if the cache is less than or equal to 30 mins old
    If it is, it will return it as it is.
    If it isn't, it will delete the expired cache from the file and return None
    If the file doesn't exist at all it will return None
    """
    if not cache:
        return
    file = os.path.join(TEMP_FOLDER, 'selenium_cached_requests.json')
    if os.path.isfile(file):

        with open(file, 'r') as f:
            data = json.load(f)

        # Yes, this is ugly,
        # but its the best way that I found to find the cache
        # when the url is not exactly the same (a slash at the end or not)
        clean_url = (url[:-1] if url and url[-1] == '/' else url)
        found = False

        for link in data:
            if link == clean_url:
                url = link
                found = True

        if not found:
            return

        timestamp = data[url]['expiry']

        if (time.time() - timestamp <= 1800):
            return data[url]
        else:
            data.pop(url, None)

            with open(file, 'w') as f:
                json.dump(data, f, indent=4)


def driver_select():
    '''
    This configures what each browser should do
    and returns the corresponding driver.
    '''
    browser = get_browser_config()
    data_dir = get_data_dir()
    executable = get_browser_executable()
    binary = get_driver_binary()

    if browser == 'firefox':
        fireFox_Options = webdriver.FirefoxOptions()
        ops = [
            "--width=1920", "--height=1080",
            "-headless", "--log fatal"
        ]

        for option in ops:
            fireFox_Options.add_argument(option)

        fireFox_Profile = webdriver.FirefoxProfile()
        fireFox_Profile.set_preference(
            "general.useragent.override", get_random_header()['user-agent']
        )

        driver = webdriver.Firefox(
            # sets user-agent
            firefox_profile=fireFox_Profile,
            # sets various firefox settings
            options=fireFox_Options,
            # by default it will be None, if a binary location is in the config then it will use that
            firefox_binary=None if not executable else executable,
            # by default it will be "geckodriver", if a geckodriver location is in the config then it will use that
            executable_path=(binary if binary else "geckodriver"),
            # an attempt at stopping selenium from printing a pile of garbage to the console.
            service_log_path=os.path.devnull
        )

    elif browser == 'chrome':
        from selenium.webdriver.chrome.options import Options

        profile_path = os.path.join(data_dir, 'Selenium_chromium')
        chrome_options = Options()

        ops = [
            "--headless", "--disable-gpu", '--log-level=OFF',
            f"--user-data-dir={profile_path}", "--no-sandbox",
            "--window-size=1920,1080", f"user-agent={get_random_header()['user-agent']}"  # noqa
        ]

        for option in ops:
            chrome_options.add_argument(option)

        cap = None

        if executable:
            from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

            cap = DesiredCapabilities.CHROME
            cap['binary_location'] = executable

        driver = webdriver.Chrome(
            # sets user-agent, and various chrome settings
            options=chrome_options,
            # by default it will be "chromedriver", if a chromedriver location is in the config then it will use that
            executable_path=(binary if binary else "chromedriver"),
            # by default it will be None, if a binary location is in the config then it will use that
            desired_capabilities=cap,
            # an attempt at stopping selenium from printing a pile of garbage to the console.
            service_log_path=os.path.devnull
        )
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
    abort_after = 50  # seconds
    start = time.time()

    title = driver.title  # title = "Just a moment..."
    while "Just a moment" in title:
        time.sleep(0.35)
        delta = time.time() - start
        if delta >= abort_after:
            logger.error(f'Timeout:\tCouldnt bypass cloudflare. \
            See the screenshot for more info:\t{get_data_dir()}/screenshot.png')
            return 1
        title = driver.title
        if not "Just a moment" in title:
            break
    time.sleep(2)  # This is necessary to make sure everything has loaded fine.
    return 0


def request(request_type, url, **kwargs):  # Headers not yet supported , headers={}
    params = kwargs.get('params', {})

    url = url if not params else url + '?' + urlencode(params)
    cached_data = check_cache(url)

    if cached_data:
        text = cached_data['data']
        user_agent = cached_data['user_agent']
        request_type = cached_data['method']
        cookies = cached_data['cookies']
        return SeleResponse(url, request_type, text, cookies, user_agent)

    else:
        driver = driver_select()
        driver.get(url)

        try:
            exit_code = cloudflare_wait(driver)
            user_agent = driver.execute_script("return navigator.userAgent;")
            cookies = driver.get_cookies()
            text = driver.page_source
            driver.close()

            if exit_code != 0:
                return SeleResponse(url, request_type, None, cookies, user_agent)

            seleResponse = SeleResponse(
                url, request_type,
                text, cookies,
                user_agent
            )

            cache_request(seleResponse)
            return seleResponse

        except:
            driver.save_screenshot(f"{get_data_dir()}/screenshot.png")
            driver.close()
            logger.error(f'There was a problem getting the page: {url}.' +
                         '\nSee the screenshot for more info:\t{get_data_dir()}/screenshot.png')
            return


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
        return '<SeleResponse URL: {} METHOD: {} TEXT: {} COOKIES: {} USERAGENT: {}>'.format(
            self.url, self.method, self.text, self.cookies, self.user_agent)
