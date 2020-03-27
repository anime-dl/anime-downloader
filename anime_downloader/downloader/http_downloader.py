import os
import copy
import logging

from anime_downloader.downloader.base_downloader import BaseDownloader
from anime_downloader import session
import requests
import requests_cache

session = session.get_session()
session = requests
logger = logging.getLogger(__name__)


class HTTPDownloader(BaseDownloader):
    def _download(self):
        logger.warning('Using internal downloader which might be slow. Use aria2 for full bandwidth.')
        if self.range_size is None:
            self._non_range_download()
        else:
            self._ranged_download()

    def _ranged_download(self):
        http_chunksize = self.range_size

        range_start = 0
        range_end = http_chunksize

        url = self.source.stream_url
        headers = {
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101Firefox/56.0",
        }
        if self.source.referer:
            headers['Referer'] = self.source.referer

        # Make a new file, maybe not the best way
        with open(self.path, 'w'):
            pass

        r = session.get(url, headers=headers, stream=True)
        while self.downloaded < self._total_size:
            r = session.get(url,
                            headers=set_range(range_start, range_end, headers),
                            stream=True)
            if r.status_code == 206:
                with open(self.path, 'ab') as f:
                    for chunk in r.iter_content(chunk_size=self.chunksize):
                        if chunk:
                            f.write(chunk)
                            self.report_chunk_downloaded()

            if range_end == '':
                break
            range_start = os.stat(self.path).st_size
            range_end += http_chunksize
            if range_end > self._total_size:
                range_end = ''

    def _non_range_download(self):
        url = self.source.stream_url
        headers = {
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101Firefox/56.0",
        }
        if self.source.referer:
            headers['Referer'] = self.source.referer
        r = session.get(url, headers=headers, stream=True)

        if r.status_code == 200:
            with open(self.path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=self.chunksize):
                    if chunk:
                        f.write(chunk)
                        self.report_chunk_downloaded()


def set_range(start=0, end='', headers=None):
    if headers is None:
        headers = {}
    headers = copy.copy(headers)

    headers['Range'] = 'bytes={}-{}'.format(start, end)
    return headers
