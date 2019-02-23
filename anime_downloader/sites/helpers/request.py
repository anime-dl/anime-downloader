# TODO: Check without node installed
# cfscrape is a necessery dependency
import cfscrape
import logging
from bs4 import BeautifulSoup

from anime_downloader import session

__all__ = [
    'get',
    'post',
    'soupfiy',
]

logger = logging.getLogger(__name__)

req_session = session.get_session()
cf_session = session.get_session(cfscrape.create_scraper())


def get(url: str,
        cf: bool = True,
        **kwargs):
    '''
    get performs a get request
    '''
    # TODO: Add headers
    sess = cf_session if cf else req_session
    res = sess.get(url, **kwargs)
    # TODO: check status codes
    return res


def post(url: str,
        cf: bool = True,
        **kwargs):
    '''
    get performs a get request
    '''
    # TODO: Add headers
    sess = cf_session if cf else req_session
    res = sess.post(url, **kwargs)
    # TODO: check status codes
    return res


def soupfiy(res):
    # TODO: res datatype
    """soupfiy Beautiful soups response object of request

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
