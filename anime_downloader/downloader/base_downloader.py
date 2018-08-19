import os
import requests
import time
import logging
import sys

from anime_downloader import util


class BaseDownloader:
    def __init__(self, source, path, force, range_size=None):
        logging.info(path)

        self.url = source.stream_url
        self.referer = source.referer
        self.path = path
        self.range_size = range_size

        util.make_dir(path.rsplit('/', 1)[0])

        self.chunksize = 16384

        r = requests.get(self.url, stream=True)

        self.total_size = int(r.headers['Content-length'])
        if os.path.exists(path):
            if abs(os.stat(path).st_size - self.total_size)<10 and not force:
                logging.warning('File already downloaded. Skipping download.')
                return
            else:
                os.remove(path)

    def download(self):
        self.pre_process()

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
        write_status(self.downloaded, self.total_size, self.start_time)


def write_status(downloaded, total_size, start_time):
    elapsed_time = time.time()-start_time
    rate = (downloaded/1024)/elapsed_time if elapsed_time else 'x'
    downloaded = float(downloaded)/1048576
    total_size = float(total_size)/1048576

    status = 'Downloaded: {0:.2f}MB/{1:.2f}MB, Rate: {2:.2f}KB/s'.format(
        downloaded, total_size, rate)

    sys.stdout.write("\r" + status + " "*5 + "\r")
    sys.stdout.flush()
