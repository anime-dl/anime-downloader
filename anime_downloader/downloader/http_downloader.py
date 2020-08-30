import os
import copy
import logging
import time
import math
import sys
import json

from anime_downloader.downloader.base_downloader import BaseDownloader
import requests
import requests_cache
import multiprocessing as mp

session = requests.Session()
session.stream = True
session.verify = False
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

        self.number_of_threads = 8

        if not self._total_size:
            logger.info('Unknown file size.')

        logger.info('Starting download.')
        self.start_time = time.time()
        # To get reliable feedback from the threads it uses a dict containing all the info on the threads.
        # This allows maximum download and resumption if any of the threads fail halfway.

        # Init a process manager
        manager = mp.Manager()
        q = manager.Queue()
        pool = mp.Pool(mp.cpu_count() + 2)

        self.thread_report = manager.dict()

        self.number_of_threads = self.number_of_threads if self._total_size > self.chunksize*self.number_of_threads else 1

        partfile = "".join(os.path.abspath(self.path).split('.')[:-1])+'.part'
        if os.path.isfile(partfile):
            logger.info('Resuming download.')
            with open(partfile,"r") as metadata:
                metadata = json.load(metadata)
                self.number_of_threads = metadata.get('threads', self.number_of_threads)
                self.chunksize = metadata.get('chunksize', self.chunksize)
                for i in metadata:
                    if i.isnumeric() and type(metadata[i]) is dict:
                        if type(metadata[i].get('chunks')) is int:
                            self.thread_report[int(i)] = manager.dict()
                            #self.thread_report[int(i)]['start'] = self.chunksize*metadata[i]['chunks']
                            self.downloaded += self.chunksize*metadata[i]['chunks']
                            self.thread_report[int(i)]['chunks'] = metadata[i]['chunks']
                            self.thread_report[int(i)]['len'] = metadata[i]['len']

        if not os.path.isfile(self.path):
            maxsize = int(sys.maxsize/10)
            with open(self.path, "wb") as fp:
                logger.info('Preparing file.')
                if self._total_size >= maxsize:
                    threads = math.floor(self._total_size/maxsize)
                    for i in range(threads):
                        if i+1 == threads:
                            fp.write(b'0'*(self._total_size-(maxsize*(i+1)-maxsize*i)*i))
                        else:
                            fp.write(b'0'*(maxsize*(i+1) - maxsize*i))
                else:
                    fp.write(b'0' * self._total_size)

        logger.info('Using {} thread{}.'.format(self.number_of_threads, (self.number_of_threads > 1) *'s'))
        self.part = math.floor(self._total_size / self.number_of_threads)

        # Prepares the threads with starting info.
        for i in range(self.number_of_threads):
            if not self.thread_report.get(i):
                self.thread_report[i] = manager.dict()

            if not self.thread_report[i].get('start'):
                start = int(self.part*i)
                self.thread_report[i]['start'] = start
            
            if not self.thread_report[i].get('chunks'):
                self.thread_report[i]['chunks'] = 0

            # Ensures non-overlapping downloads.
            if i + 1 == self.number_of_threads:
                end = self._total_size
            else:
                end = int(self.part*(i+1))-1
            
            self.thread_report[i]['len'] = 0
            self.thread_report[i]['end'] = end
            self.thread_report[i]['done'] = False

        jobs = []
        # Starts a consumer which writes to the file.
        consumer = pool.apply_async(self.consumer, (q,))

        # Arbitrary max tries, somewhat high number.
        for attempt in range(self.number_of_threads*2):
            for i in range(self.number_of_threads):
                # If the thread chunck is done it'll do nothing.
                # May not be optimal, but better threading would be too complex.
                if self.thread_report[i].get('done'):
                    continue

                start = self.thread_report[i]['start']
                # Start gets offset based on the previous downloaded chunks.
                start += (self.thread_report[i].get('chunks',0)*self.chunksize)
                end = self.thread_report[i]['end']
                # Just in case, creating tons of threads at once seems to cause issues.
                time.sleep(0.2)
                job = pool.apply_async(self.thread_downloader, (url, start, end, headers, i, q,))
                jobs.append(job)

            for job in jobs:
                job.get()

        # Kill the consumer
        q.put('kill')
        pool.close()
        pool.join()


    def _non_range_download(self):
        url = self.source.stream_url
        headers = {
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101Firefox/56.0",
        }
        if self.source.referer:
            headers['Referer'] = self.source.referer
        r = session.get(url, headers=headers)

        if r.status_code == 200:
            with open(self.path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=self.chunksize):
                    if chunk:
                        f.write(chunk)
                        self.report_chunk_downloaded()


    def thread_downloader(self, url, start, end, headers, number, q):
        if end:
            headers['Range'] = 'bytes=%d-%d' % (start, end)

        # specify the starting and ending of the file
        # request the specified part and get into variable
        with session.get(url, headers=headers) as r:
            try:
                r.raise_for_status()
            except:
                return

            if not (r.headers.get('content-length') or
                    r.headers.get('Content-length') or
                    r.headers.get('Content-Length') or
                    r.headers.get('Transfer-Encoding') == 'chunked') or 'text/html' in r.headers.get('Content-Type',''):
                return

            for chunk in r.iter_content(chunk_size=self.chunksize):
                if chunk:
                    q.put((start, chunk, number))

            self.thread_report[number]['done'] = True


    def consumer(self, q):
        # ANY ERRORS HERE ARE SILENT.

        """Listen to consumer queue and write file using offset
        :param q: Consumer queue
        """
        f = open(self.path, 'r+b')
        partfile = "".join(os.path.abspath(self.path).split('.')[:-1])+'.part'
        metadata = open(partfile, "w+")
        metadata.write('{}')

        meta = {}
        meta['threads'] = self.number_of_threads
        meta['chunksize'] = self.chunksize

        for i in range(self.number_of_threads):
            meta[i] = {}
            meta[i]['chunks'] = self.thread_report[i]['chunks']
            meta[i]['len'] = 0

        while 1:
            m = q.get()
            if m == 'kill':
                break
            start, chunk, number = m
            offset = start+(meta[number]['len'])

            if chunk:
                f.seek(offset)
                f.write(chunk)
                meta[number]['len'] += len(chunk)
                self.thread_report[number]['len'] += len(chunk)
                meta[number]['chunks'] += 1
            metadata.seek(0)
            json.dump(meta, metadata)
            metadata.truncate()

            self.thread_report[number]['chunks'] += 1
            self.report_chunk_downloaded()

            f.flush()

        f.close()
        metadata.close()
        return self.thread_report


def set_range(start=0, end='', headers=None):
    if headers is None:
        headers = {}
    headers = copy.copy(headers)

    headers['Range'] = 'bytes={}-{}'.format(start, end)
    return headers
