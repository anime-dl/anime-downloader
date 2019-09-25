import os

from anime_downloader.downloader.base_downloader import BaseDownloader
from anime_downloader import session

session = session.get_session()


class HTTPDownloader(BaseDownloader):
    def _download(self):
        if self.options['range_size'] is None:
            self._non_range_download()
        else:
            self._ranged_download()

    def _ranged_download(self):
        http_chunksize = self.options['range_size']

        range_start = 0
        range_end = http_chunksize

        # Make a new file, maybe not the best way
        with open(self.path, 'w'):
            pass

        r = session.get(self.url, headers={
                        'referer': self.referer}, stream=True)
        while self.downloaded < self.total_size:
            r = session.get(self.url,
                            headers=set_range(
                                range_start, range_end, self.referer),
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
            if range_end > self.total_size:
                range_end = ''

    def _non_range_download(self):
        r = session.get(self.url, headers={
                        'referer': self.referer}, stream=True)

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
        'referer': referer
    }

    headers['Range'] = 'bytes={}-{}'.format(start, end)
    return headers
