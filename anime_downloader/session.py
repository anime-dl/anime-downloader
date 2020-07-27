import logging
import os

import requests
import requests_cache
import urllib3
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import tempfile


logger = logging.getLogger(__name__)

cachefile = os.path.join(tempfile.gettempdir(), 'anime-cache')
# requests_cache.install_cache(cachefile, backend='sqlite', expire_after=3600)

_session = requests_cache.CachedSession(cachefile, backend='sqlite', expire_after=3600)

# _session = requests.Session()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_session(custom_session=None):
    global _session

    if custom_session:
        custom_session.verify = _session.verify
        _session = custom_session
    # else:
    #     _session = _session or requests.Session()

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
                "5M", "--referer", "{referer}", "--max-overall-download-limit=", "{speed_limit}"
            ],
            "_disable_ssl_additional": ["--check-certificate", "false"],
        },
    }
    _cache = {}

    def __init__(self):
        # TODO: Figure out a way to do disable_ssl elgantly
        # Disablining ssl check should be in session and not in
        # donwloader because it's a session wise option

        # TODO: Add ability to add downloaders using config
        pass

    def get(self, key, **options):
        # HACK: Because of circular dependency
        from anime_downloader import downloader
        # HACK: This has to obtained like this because this variable is
        # set inside dl. There should be a persistant data store throughout
        # the app instead.
        disable_ssl = get_session().verify
        if key not in self._cache:
            if key == 'http':
                self._cache[key] = downloader.get_downloader('http')()
            if disable_ssl:
                if '_disable_ssl_additional' in self.external_downloaders[key]:
                    self.external_downloaders[key]['cmd_opts'] = {
                        **self.external_downloaders[key]['cmd_opts'],
                        **self.external_downloaders[key]['_disable_ssl_additional']
                    }
            self._cache[key] = downloader.get_downloader('ext')(
                options=self.external_downloaders[key])
        return self._cache[key]
