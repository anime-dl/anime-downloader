import os
import time
import logging
import sys

from anime_downloader import util
import requests

logger = logging.getLogger(__name__)


class BaseDownloader:
    def __init__(self, source, path, force, range_size, callback=None):
        self.chunksize = 16384
        self._total_size = None
        self.source = source
        self.path = path
        self.resumed = 0
        # these should be included in a options dict, maybe
        self.force = force
        self.range_size = range_size

        if callback is None:
            callback = write_status
        self.callback = callback
        self.thread_report = []

    def check_if_exists(self):
        # Added Referer Header as kwik needd it.
        headers = self.source.headers
        if 'user-agent' not in headers:
            headers['user-agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101Firefox/56.0"

        if self.source.referer:
            headers['referer'] = self.source.referer

        # I couldn't figure out how to retry based on headers (comment below) with httpadapter.
        # if not self._total_size and not r.headers.get('Transfer-Encoding') == 'chunked':
        for i in range(5):
            with requests.get(self.source.stream_url, headers=headers, stream=True, verify=False) as r:
                self._total_size = max(int(r.headers.get('Content-length', 0)), 
                                        int(r.headers.get('Content-Length', 0)), 
                                        int(r.headers.get('content-length', 0)))
                if not self._total_size and not r.headers.get('Transfer-Encoding') == 'chunked':
                    continue


                partfile = os.path.splitext(self.path)[0]+'.part'
                if os.path.exists(self.path):
                    if abs(os.stat(self.path).st_size - self._total_size) < 10 \
                       and not self.force and not os.path.isfile(partfile):
                        logger.warning('File already downloaded. Skipping download.')
                        return True
                    else:
                        # NOTE: Cannot resume downloads with unknown size.
                        if not abs(os.stat(self.path).st_size - self._total_size) < 10:
                            logger.error('Total size mismatch ({} and {}), the file already downloaded probably comes from a different source.'.format(
                                        self._total_size, abs(os.stat(self.path).st_size)))
                            sys.exit(1)
        logger.debug('Total size: ' + str(self._total_size))


    def download(self):
        # TODO: Clean this up
        self.pre_process()
        logger.info(self.path)

        # TODO: Use pathlib. Break into functions
        util.make_dir(self.path.rsplit('/', 1)[0])

        # Goes to the next episode if the file already exists.
        if self.check_if_exists():
            return

        self.downloaded = 0
        self._download()
        self.post_process()

    def _download(self):
        raise NotImplementedError

    def pre_process(self):
        pass

    def post_process(self):
        pass

    def report_chunk_downloaded(self, chunksize):
        self.downloaded += chunksize
        self.callback(self.downloaded, self._total_size, self.start_time, self.resumed)


def write_status(downloaded, total_size, start_time, resumed):
    elapsed_time = time.time()-start_time
    rate = (downloaded/1024)/elapsed_time if elapsed_time else 'x'
    downloaded = float(downloaded+resumed)/1048576
    total_size = float(total_size)/1048576

    eta = ((total_size-downloaded)*1024)/rate
    minutes = '0' * (round((eta-(eta%60))/60) < 10) + str(round((eta-(eta%60))/60))
    seconds = '0' * (round(eta%60) < 10) + str(round(eta%60))
    eta = f'{minutes}:{seconds}'
    if downloaded >= total_size:
        #downloaded = total_size
        eta = 'Done'

    if total_size:
        status = 'Downloaded: {0:.2f}MB/{1:.2f}MB, Rate: {2:.2f}KB/s, ETA: {3}'.format(
            downloaded, total_size, rate, eta)

    # Chunked transfer, unknown size?
    else:
        status = 'Downloaded: {0:.2f}MB, Rate: {1:.2f}KB/s'.format(downloaded, rate)

    sys.stdout.write("\r" + status + " "*5 + "\r")
    sys.stdout.flush()
