import os
import logging

from anime_downloader.downloader.base_downloader import BaseDownloader
from anime_downloader import session

session = session.get_session()


class HTTPDownloader(BaseDownloader):
    def _download(self):
        if os.path.exists(self.path):
            # Handle both cases where user will still want file downloaded
            # even if it exists
            if abs(os.stat(self.path).st_size - self.total_size) < 10 and not self.force:
                logging.warning('File already downloaded. Skipping download.')
                return
            elif self.force:
                os.remove(self.path)

        if self.range_size is None:
            self._non_range_download()
        else:
            self._ranged_download()

    def pre_process(self):
        self.downloaded = 0
        # Preprocess ranges and amount downloaded for ranged download
        if self.range_size:
            if not os.path.exists(self.path):
                self._range_start = 0
                self.downloaded = 0
                self._range_end = self.range_size

                # Make a new file, maybe not the best way
                with open(self.path, 'w'):
                    pass
            else:
                self._range_start = os.stat(self.path).st_size
                self._range_end = self._range_start + self.range_size
                self.downloaded = self._range_start

    def _ranged_download(self):
        http_chunksize = self.range_size

        range_start = self._range_start
        range_end = self._range_end

        with open(self.path, 'ab') as f:
            while self.downloaded < self.total_size:
                r = session.get(self.url,
                                headers=set_range(range_start, range_end, self.referer),
                                stream=True)
                if r.status_code == 206:
                        for chunk in r.iter_content(chunk_size=self.chunksize):
                            if chunk:
                                f.write(chunk)
                                self.report_chunk_downloaded()

                if range_end == '':
                    break
                range_start = os.stat(self.path).st_size
                range_end = range_start + http_chunksize
                if range_end > self.total_size:
                    range_end = ''

    def _non_range_download(self):
        r = session.get(self.url, headers={'referer': self.referer}, stream=True)

        if r.status_code == 200:
            with open(self.path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=self.chunksize):
                    if chunk:
                        f.write(chunk)
                        self.report_chunk_downloaded()


def set_range(start=0, end='', referer=None):
    headers = {
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101"
                  "Firefox/56.0",
    'referer'   : referer
    }

    headers['Range'] = 'bytes={}-{}'.format(start, end)
    return headers
