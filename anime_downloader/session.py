import logging

import requests
import requests_cache
import urllib3
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import tempfile

from anime_downloader import downloader

logger = logging.getLogger(__name__)

file = tempfile.mktemp()
requests_cache.install_cache('anime_downloader', expires_after=300, location=file)

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


class DownloaderSession:
    external_downloaders = {
        "aria2": {
            "executable": "aria2c",
            "cmd_opts": [
                "{stream_url}", "-x", "12", "-s", "12",
                "-j", "12", "-k", "10M", "-o", "{file_format}",
                "--continue", "true", "--dir", "{download_dir}",
                "--stream-piece-selector", "inorder", "--min-split-size",
                "5M", "--referer", "{referer}"
            ],
            "_disable_ssl_additional": ["--check-certificate", "false"],
        },
    }

    def __init__(self, disable_ssl=False):
        # TODO: Figure out a way to do disable_ssl elgantly
        # Disablining ssl check should be in session and not in
        # donwloader because it's a session wise option

        # TODO: Add ability to add downloaders using config
        pass

    def __getitem__(self, key):
        if key == 'http':
            return downloader.get_downloader('http')()
        return self.down
