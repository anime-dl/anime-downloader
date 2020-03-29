import os
import time
import logging
import sys

from anime_downloader import util
from anime_downloader import session

logger = logging.getLogger(__name__)


class BaseDownloader:
    def __init__(self, source, path, force, range_size, callback=None):
        self.chunksize = 16384
        self._total_size = None
        self.source = source
        self.path = path

        # these should be included in a options dict, maybe
        self.force = force
        self.range_size = range_size

        if callback is None:
            callback = write_status
        self.callback = callback

    def check_if_exists(self):
        # Added Referer Header as kwik needd it.
        headers = {
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101Firefox/56.0",
        }
        if self.source.referer:
            headers['referer'] = self.source.referer
        r = session.get_session().get(
            self.source.stream_url, headers=headers, stream=True)

        self._total_size = int(r.headers['Content-length'])
        logger.debug('total size: ' + str(self._total_size))
        if os.path.exists(self.path):
            if abs(os.stat(self.path).st_size - self._total_size) < 10 \
               and not self.force:
                logger.warning('File already downloaded. Skipping download.')
                return
            else:
                os.remove(self.path)

    def download(self):
        # TODO: Clean this up
        self.pre_process()
        logger.info(self.path)

        # TODO: Use pathlib. Break into functions
        util.make_dir(self.path.rsplit('/', 1)[0])

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
        self.callback(self.downloaded, self._total_size, self.start_time)


def write_status(downloaded, total_size, start_time):
    elapsed_time = time.time()-start_time
    rate = (downloaded/1024)/elapsed_time if elapsed_time else 'x'
    downloaded = float(downloaded)/1048576
    total_size = float(total_size)/1048576

    status = 'Downloaded: {0:.2f}MB/{1:.2f}MB, Rate: {2:.2f}KB/s'.format(
        downloaded, total_size, rate)

    sys.stdout.write("\r" + status + " "*5 + "\r")
    sys.stdout.flush()
