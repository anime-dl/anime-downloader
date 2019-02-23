# TODO: Check without node installed
# cfscrape is a necessery dependency
import cfscrape
import logging
from bs4 import BeautifulSoup

from anime_downloader import session
from anime_downloader.const import get_random_header

__all__ = [
    'get',
    'post',
    'soupify',
]

logger = logging.getLogger(__name__)

req_session = session.get_session()
cf_session = cfscrape.create_scraper(sess=req_session)
default_headers = get_random_header()


def get(url: str,
        cf: bool = True,
        referer: str = None,
        headers=None,
        **kwargs):
    '''
    get performs a get request
    '''
    # TODO: Refactor
    sess = cf_session if cf else req_session
    if headers:
        default_headers.update(headers)
    if referer:
        default_headers['Referer'] = referer
    logger.debug(default_headers)
    res = sess.get(url, headers=default_headers, **kwargs)
    res.raise_for_status()
    logger.debug(res.text)
    return res


def post(url: str,
         cf: bool = True,
         referer: str = None,
         headers=None,
         **kwargs):
    '''
    get performs a get request
    '''
    # TODO: Add headers
    sess = cf_session if cf else req_session
    if headers:
        default_headers.update(headers)
    if referer:
        default_headers['referer'] = referer
    res = sess.post(url, headers=default_headers, **kwargs)
    res.raise_for_status()
    return res


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
    soup = BeautifulSoup(res.text, 'html.parser')
    return soup
