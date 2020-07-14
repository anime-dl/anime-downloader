# TODO: Check without node installed
# cfscrape is a necessery dependency
import cfscrape
import logging
from bs4 import BeautifulSoup
import tempfile
import os
import requests

from anime_downloader import session
from anime_downloader.const import get_random_header

__all__ = [
    'get',
    'post',
    'soupify',
]

logger = logging.getLogger(__name__)

req_session = session.get_session()
cf_session = cfscrape.create_scraper()
default_headers = get_random_header()
temp_dir = tempfile.mkdtemp(prefix='animedl')
logger.debug(f"HTML file temp_dir: {temp_dir}")


def setup(func):
    """
    setup is a decorator which takes a function
    and converts it into a request method
    """
    def setup_func(url: str,
                   cf: bool = False,
                   sel: bool = False,
                   referer: str = None,
                   headers=None,
                   **kwargs):
        '''
        {0} performs a {0} request

        Parameters
        ----------
        url : str
            url is the url of the request to be performed
        cf : bool
            cf if True performs the request through cfscrape.
            For cloudflare protected sites.
        referer : str
            a url sent as referer in request headers
        '''
        selescrape = None
        if cf:
            sess = cf_session
        elif sel:
            try:
                from selenium import webdriver
                from anime_downloader.sites.helpers import selescrape
                sess = selescrape
            except ImportError:
                sess = cf_session
                logger.warning("This provider may not work correctly because it requires selenium to work.\nIf you want to install it then run:  'pip install selenium' .")
        else: 
            sess = req_session 

        if headers:
            default_headers.update(headers)
        if referer:
            default_headers['referer'] = referer

        logger.debug('-----')
        logger.debug('{} {}'.format(func.__name__.upper(), url))
        logger.debug(kwargs)
        logger.debug(default_headers)
        logger.debug('-----')

        res = sess.request(func.__name__.upper(),
                           url,
                           headers=default_headers,
                           **kwargs)

        if sess != selescrape: #TODO fix this for selescrape too
            res.raise_for_status()
            logger.debug(res.url)
            # logger.debug(res.text)
            if logger.getEffectiveLevel() == logging.DEBUG:
                _log_response_body(res)
        return res

    setup_func.__doc__ = setup_func.__doc__.format(func.__name__)
    return setup_func


@setup
def get(url: str,
        cf: bool = False,
        referer: str = None,
        headers=None,
        **kwargs):
    '''
    get performs a get request

    Parameters
    ----------
    url : str
        url is the url of the request to be performed
    cf : bool
        cf if True performs the request through cfscrape.
        For cloudflare protected sites.
    referer : str
        a url sent as referer in request headers
    '''


@setup
def post(url: str,
         cf: bool = False,
         referer: str = None,
         headers=None,
         **kwargs):
    '''
    post performs a post request

    Parameters
    ----------
    url : str
        url is the url of the request to be performed
    cf : bool
        cf if True performs the request through cfscrape.
        For cloudflare protected sites.
    referer : str
        a url sent as referer in request headers
    '''


def soupify(res):
    # TODO: res datatype
    """soupify Beautiful soups response object of request

    Parameters
    ----------
    res :
        res is `request.response`

    Returns
    -------
    BeautifulSoup.Soup
    """
    if isinstance(res, requests.Response):
        res = res.text
    soup = BeautifulSoup(res, 'html.parser')
    return soup


def _log_response_body(res):
    import json
    import pathlib
    file = tempfile.mktemp(dir=temp_dir)
    logger.debug(file)
    with open(file, 'w', encoding="utf-8") as f:
        f.write(res.text)

    data_file = temp_dir + '/data.json'
    if not os.path.exists(data_file):
        with open(data_file, 'w') as f:
            json.dump([], f)
    data = None
    with open(data_file, 'r') as f:
        data = json.load(f)
        data.append({
            'method': res.request.method,
            'url': res.url,
            'file': pathlib.Path(file).name,
        })
    with open(data_file, 'w') as f:
        json.dump(data, f)
