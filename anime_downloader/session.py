import requests
import urllib3
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import requests_cache

import logging

logger = logging.getLogger(__name__)

requests_cache.install_cache('anime_downloader', expires_after=300)

_session = requests_cache.CachedSession()

# _session = requests.Session()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_session(custom_session=None):
    global _session

    if custom_session:
        custom_session.verify = _session.verify
        _session = custom_session
    else:
        _session = _session or requests.Session()

    retry = Retry(
        total=10,
        read=10,
        connect=10,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504,)
    )
    adapter = HTTPAdapter(max_retries=retry)
    _session.mount('http://', adapter)
    _session.mount('https://', adapter)

    def hook(response, *args, **kwargs):
        if not getattr(response, 'from_cache', False):
            logger.debug('uncached request')
        else:
            logger.debug('cached request')
        return response
    _session.hooks = {'response': hook}

    return _session
