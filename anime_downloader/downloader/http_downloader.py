import os
import copy
import logging
import threading
import time
import math
import sys

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
        headers = self.source.headers
        if 'user-agent' not in headers:
            headers['user-agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101Firefox/56.0",

        if self.source.referer:
            headers['Referer'] = self.source.referer

        # This whole block is just a very elaborate way of writing a file full of zeroes in a safe way.
        # On 32-bit simply doing     fp.write(b'0' * self._total_size)    on a 3gb file throws errors.
        # Doing it in chunks however works.
        # sys.maxsize/10 is an arbitrary number I judged as safe. (even sys.maxsize/2 works)

        # This error doesn't affect downloading the actual file as the writing is done in chunks.

        maxsize = int(sys.maxsize/10)
        with open(self.path, "wb") as fp:
            logger.info('Preparing file.')
            if self._total_size >= maxsize:
                max_writes = int(math.ceil(self._total_size/maxsize))
                for chunk in range(max_writes):
                    if chunk + 1 == max_writes:
                        fp.write(b'0' * int(self._total_size%((max_writes-1)*maxsize)))
                    else:
                        fp.write(b'0' * maxsize)
            else:
                fp.write(b'0' * self._total_size)

        number_of_threads = 8
        logger.info('Using {} thread{}.'.format(number_of_threads, (number_of_threads > 1) *'s'))

        # Creates an empty part file, this comes at the cost of not really knowing if a file is fully completed.
        # We could possibly add some end bytes on completion?

        self.part = math.floor(self._total_size / number_of_threads)

        logger.info('Starting download.')
        self.start_time = time.time()
        # To get reliable feedback from the threads it uses a dict containing all the info on the threads.
        # This allows maximum download and resumption if any of the threads fail halfway.

        self.thread_report = {}
        # Prepares the threads with starting info.
        for i in range(number_of_threads):
            self.thread_report[i] = {}
            start = int(self.part*i)

            # Ensures non-overlapping downloads.
            if i + 1 == number_of_threads:
                end = self._total_size
            else:
                end = int(self.part*(i+1))-1

            self.thread_report[i]['start'] = start
            self.thread_report[i]['end'] = end
            self.thread_report[i]['chunks'] = 0
            self.thread_report[i]['done'] = False

        # Arbitrary max tries, somewhat high number.
        for attempt in range(number_of_threads*4):
            for i in range(number_of_threads):
                # If the thread chunck is done it'll do nothing.
                # May not be optimal, but better threading would be too complex.
                if self.thread_report[i].get('done'):
                    continue

                start = self.thread_report[i]['start']
                # Start gets offset based on the previous downloaded chunks.
                start += (self.thread_report[i].get('chunks',0)*self.chunksize)
                end = self.thread_report[i]['end']

                t = threading.Thread(target=self.thread_downloader,
                    kwargs={'url': url, 'start':start, 'end': end, 'headers':headers, 'number':i})
                t.setDaemon(True)
                t.start()

            main_thread = threading.current_thread()
            for t in threading.enumerate():
                if t is main_thread:
                    continue
                t.join()

        """
        # Collects all the files and places them in one.
        # Doesn't work correctly!!!
        with open(self.path, "wb") as file:
            for i in range(number_of_threads):
                with open(self.path+"_"+str(i), "rb") as part:
                    part.seek(int(self.part*i))
                    #var = part.tell()
                    data = part.read()
                    file.write(data)
                #os.remove(self.path+"_"+str(i))
        """

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


    def thread_downloader(self, url, start, end, headers, number):
        headers['Range'] = 'bytes=%d-%d' % (start, end) 
        # specify the starting and ending of the file
        # request the specified part and get into variable
        with requests.get(url, headers=headers, stream=True, verify=False) as r:
            if not (r.headers.get('content-length') or 
                    r.headers.get('Content-length') or 
                    r.headers.get('Content-Length')) or r.status_code not in [200, 206]:
                return False

            with open(self.path, "r+b") as fp:
                fp.seek(start)
                for chunk in r.iter_content(chunk_size=self.chunksize):
                    if chunk:
                        fp.write(chunk)
                        self.thread_report[number]['chunks'] += 1
                        self.report_chunk_downloaded()

            self.thread_report[number]['done'] = True


def set_range(start=0, end='', headers=None):
    if headers is None:
        headers = {}
    headers = copy.copy(headers)

    headers['Range'] = 'bytes={}-{}'.format(start, end)
    return headers
