import os
import time
import logging
import sys

from anime_downloader import util
from anime_downloader import session

logger = logging.getLogger(__name__)


class BaseDownloader:
    def __init__(self, options=None):
        if options is None:
            options = {}
        self.options = options
        # TODO: replace
        self.referer = self.options.get('referer', '')

        self.chunksize = 16384
        self._total_size = None
        self.url = None

    def check_if_exists(self):
        # Added Referer Header as kwik needd it.
        r = session.get_session().get(
            self.url, headers={'referer': self.referer}, stream=True)

        self._total_size = int(r.headers['Content-length'])
        if os.path.exists(self.path):
            if abs(os.stat(self.path).st_size - self._total_size) < 10 \
               and not self.options['force']:
                logger.warning('File already downloaded. Skipping download.')
                return
            else:
                os.remove(self.path)

    def download(self, url, path, options=None):
        # TODO: Clean this up
        self.pre_process()
        self.url = url
        logger.info(path)

        # TODO: Use pathlib. Break into functions
        self.path = path
        util.make_dir(path.rsplit('/', 1)[0])

        if options is not None:
            self.options = {**options, **self.options}

        self.check_if_exists()

        self.start_time = time.time()
        self.downloaded = 0
        self._download()

        self.post_process()

    def _download(self):
        raise NotImplementedError

    def pre_process(self):
        pass

    def post_process(self):
        pass

    def report_chunk_downloaded(self):
        self.downloaded += self.chunksize
        write_status(self.downloaded, self._total_size, self.start_time)


def write_status(downloaded, total_size, start_time):
    elapsed_time = time.time()-start_time
    rate = (downloaded/1024)/elapsed_time if elapsed_time else 'x'
    downloaded = float(downloaded)/1048576
    total_size = float(total_size)/1048576

    status = 'Downloaded: {0:.2f}MB/{1:.2f}MB, Rate: {2:.2f}KB/s'.format(
        downloaded, total_size, rate)

    sys.stdout.write("\r" + status + " "*5 + "\r")
    sys.stdout.flush()
