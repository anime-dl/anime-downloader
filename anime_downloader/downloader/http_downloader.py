import os
import copy
import logging
import time
import math
import sys
import json
import signal

from anime_downloader.downloader.base_downloader import BaseDownloader
import requests
import requests_cache
from multiprocessing import Manager, Pool

session = requests.Session()
session.stream = True
session.verify = False
logger = logging.getLogger(__name__)

from anime_downloader.config import Config

class HTTPDownloader(BaseDownloader):
    def _download(self):
        logger.warning('Using internal downloader which might be slow. Use aria2 for full bandwidth.')
        # NOTE: Dont assume it'll always be this number.
        # It'll revert to 1 thread under certain circumstances.
        # (Unknown file size and resuming of other downloads.)
        self.number_of_threads = Config['dl']['internal_threads']
        # This makes number_of_threads 1 if the file is small enough or unknown.
        self.number_of_threads = self.number_of_threads if self._total_size > self.chunksize*self.number_of_threads else 1

        if self.range_size is None or self.number_of_threads == 1:
            self._non_thread_download()
        else:
            # Pool() doesn't work on mobile devices and gives ImportError.
            # This allows fallback to _non_thread_download()
            try:
                Pool()
                self._thread_download()
            except ImportError:
                logger.warning('Python theading is not supported on this platfrom, falling back to the non threaded downloader.')
                self._non_thread_download()


    def _thread_download(self):
        url = self.source.stream_url
        headers = self.source.headers

        # Defaults headers if not specified.
        if 'user-agent' not in headers:
            headers['user-agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101Firefox/56.0",

        if self.source.referer:
            headers['Referer'] = self.source.referer

        # If downloaded file is file.mp4 the partfile will be file.part
        self.read_partfile()
        self.create_file()

        # By this time self.number_of_threads should not be changed.
        logger.info('Using {} thread{}.'.format(self.number_of_threads, (self.number_of_threads > 1) *'s'))
        # Divides the download into parts, used for offset in writing the file.
        self.part = math.floor(self._total_size / self.number_of_threads)

        # Init a process manager
        manager = Manager()
        q = manager.Queue()
        pool = Pool(self.number_of_threads + 2)

        self.thread_report = manager.list(self.thread_report)

        """
        self.thread_report is a dict accesible from all threads used transfer info between them.
        This CAN be removed in favor of reading from the partfile when necessary which can reduce code 
        complexity at the cost of flexibility.

        self.thread_report has a layout of:
        [{'len': 1687552, 'start': 0, 'end': 23609903, 'done': False},
         {'len': 671744, 'start': 23609904, 'end': 47219807, 'done': False}]

        Where each element of the list is a dict containing info on the thread.
        'len' is the actual length of all the chunks combined used for offsets when writing.
        'start' is where the download should start, used for requests.
        'end' is where the download should end, also used for requests.
        'done' is a bool if the download is complete.
        """
        for i in range(self.number_of_threads):
            # For communicating it's absolutely essential that the dicts in the lists are also managed.
            if not len(self.thread_report) > i:
                self.thread_report.append(manager.dict())
            else:
                self.thread_report[i] = manager.dict(self.thread_report[i])

            if not self.thread_report[i].get('start'):
                self.thread_report[i]['start'] = int(self.part*i)

            if not self.thread_report[i].get('len'):
                self.thread_report[i]['len'] = 0

            # Ensures non-overlapping downloads.
            # If it's the last thread the end will always be self._total_size
            if i + 1 == self.number_of_threads:
                end = self._total_size
            else:
                end = int(self.part*(i+1))-1

            self.thread_report[i]['end'] = end
            self.thread_report[i]['done'] = False

        logger.info('Starting download.')
        # NOTE: starting the time MUST be done before starting the consumer or else it'll error.
        # The consumer uses the start time to print download progress and will (silently) error without it.
        self.start_time = time.time()

        # Starts a consumer which writes to the file.
        # Writing to the same file from multiple places isn't very reliable.
        try:
            consumer = pool.apply_async(self.consumer, (q,))
            # Arbitrary max tries, somewhat high number.
            # This resumes the download if one of the threads fail (for example due to cap on connections).
            for attempt in range(self.number_of_threads*2):
                jobs = []
                for i in range(self.number_of_threads):
                    # If the thread is done it'll do nothing.
                    # Eventually ending in only one thread downloading.
                    # Always having max threads downloading would be too complex.
                    if self.thread_report[i].get('done'):
                        continue

                    # Start gets offset based on the previous downloaded chunks.
                    start = self.thread_report[i]['start']
                    # Passing the start and offset separate (instead of adding them) is a must to 
                    # make the internal offset in the consumer consistent.
                    offset = self.thread_report[i]['len']

                    end = self.thread_report[i]['end']
                    # Starts the thread downloader.
                    job = pool.apply_async(self.thread_downloader, (url, start, end, offset, headers, i, q,))
                    jobs.append(job)

                for job in jobs:
                    job.get()

            # Kill the consumer.
            q.put('kill')
            pool.close()
            pool.join()
            # Cleans up the partfile on completed download.
            if os.path.isfile(self.partfile):
                os.remove(self.partfile)

        except KeyboardInterrupt:
            q.put('kill')
            pool.terminate()
            pool.join()
            sys.exit()


    def thread_downloader(self, url, start, end, offset, headers, number, q):
        # This try/except is critical for ctrl + c to work on windows.
        try:
            headers['Range'] = 'bytes=%d-%d' % (start+offset, end)

            # specify the starting and ending of the file
            with session.get(url, headers=headers) as r:
                try:
                    r.raise_for_status()
                except:
                    return
                # The name of the content length is inconsistent.
                if not (r.headers.get('content-length') or
                        r.headers.get('Content-length') or
                        r.headers.get('Content-Length') or
                        r.headers.get('Transfer-Encoding') == 'chunked') or 'text/html' in r.headers.get('Content-Type',''):
                    return

                for chunk in r.iter_content(chunk_size=self.chunksize):
                    if chunk:
                        # Queues up chunk for writing.
                        q.put((start, chunk, number))

                # Moving this to consumer will cause errors.
                self.thread_report[number]['done'] = True
        except KeyboardInterrupt:
            pass


    def consumer(self, q):
        # ANY ERRORS HERE ARE SILENT.
        # If there's an error in this function nothing will happen besides that the 
        # download progress won't go up.

        """Listen to consumer queue and write file using offset
        :param q: Consumer queue
        """
        
        # Opening the file as r+b is absolutely essential to continuing downloads without corrupting them.
        with open(self.path, 'r+b') as f:
            with open(self.partfile, "w+") as metadata:
                metadata.write('{}')

                # Meta is a duplicate of self.thread_report, but only includes len
                # You might think that It'd be better to just write from self.thread_report
                # but that causes a severe bottleneck (and errors it seems) compared to keeping an internal state.
                meta = {}
                # Meta looks like {0:1234, 1:100, 2:0}
                # where the key is the thread number and the value is length written.
                for i in range(self.number_of_threads):
                    meta[i] = self.thread_report[i]['len']
                logger.debug('Meta: {}'.format(meta))

                while True:
                    message = q.get()
                    if message == 'kill':
                        logger.debug('Killed consumer.')
                        break

                    # Unpacks the message from q.put()
                    start, chunk, number = message
                    if chunk:
                        # Where to write in the file.
                        offset = start+(meta[number])
                        f.seek(offset)
                        f.write(chunk)

                        meta[number] += len(chunk)
                        self.thread_report[number]['len'] += len(chunk)
                        # Writes to partfile every single chunk.
                        # Doesn't seem to slow down the downloader.
                        metadata.seek(0)
                        json.dump(meta, metadata)
                        metadata.truncate()
                        metadata.flush()

                        # Reports the the chunk is actually downloaded, causing an uptick in the progress bar.
                        self.report_chunk_downloaded(len(chunk))
                        # Makes sure the data is written directly.
                        f.flush()


    def _non_thread_download(self):
        self.number_of_threads = 1
        url = self.source.stream_url
        headers = self.source.headers

        # Defaults headers if not specified.
        if 'user-agent' not in headers:
            headers['user-agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101Firefox/56.0",

        if self.source.referer:
            headers['Referer'] = self.source.referer

        self.read_partfile()
        logger.info('Creating file')
        self.create_file()
        self.part = math.floor(self._total_size / self.number_of_threads)
        # Allows resuming download, even from threaded.
        self.start_time = time.time()
        logger.info('Starting download.')
        meta = {}
        # Internal state to write to the partfile.
        for i in range(self.number_of_threads):
            if len(self.thread_report) > i:
                offset = self.thread_report[i].get('len',0)
            else:
                offset = 0
            meta[i] = offset
        logger.debug('Meta: {}'.format(meta))

        with open(self.path, 'r+b') as f:
            with open(self.partfile, "w+") as metadata:
                metadata.write('{}')
                # This makes it possible to resume downloads regardless of partfile.
                # It downloads in chunks, but not simultaneously.
                # If there's no partfile it should do one chunk.
                for i in range(self.number_of_threads):
                    start = self.part*i
                    if i + 1 == self.number_of_threads:
                        end = self._total_size
                    else:
                        end = int(self.part*(i+1))-1

                    if len(self.thread_report) > i:
                        offset = self.thread_report[i].get('len',0)

                    headers['Range'] = 'bytes=%d-%d' % (start+offset, end)

                    with session.get(url, headers=headers, stream=True) as r:
                        if r.status_code in [200, 206]:
                            for chunk in r.iter_content(chunk_size=self.chunksize):
                                if chunk:
                                    f.seek(start+meta[i])
                                    f.write(chunk)
                                    f.flush()
                                    meta[i] += len(chunk)
                                    metadata.seek(0)
                                    json.dump(meta, metadata)
                                    metadata.truncate()
                                    metadata.flush()
                                    self.report_chunk_downloaded(len(chunk))

        # Cleans up the partfile on completed download.
        if os.path.isfile(self.partfile):
            os.remove(self.partfile)


    def read_partfile(self):
        # If there's already a partfile it tries to read it to continue the download.
        # The amout of if statements is to make it safe even if the partfile is corrupted/from another program.
        self.partfile = os.path.splitext(self.path)[0]+'.part'
        if os.path.isfile(self.partfile):
            with open(self.partfile,"r") as data:
                try:
                    metadata = json.load(data)
                    logger.debug('Partfile: {}'.format(metadata))
                    for i in metadata:
                        if i.isnumeric() and type(metadata[i]) is int:
                            if not len(self.thread_report) > int(i):
                                self.thread_report.append({})

                            # Adds to the downloaded (to make the progress show up properly).
                            self.resumed += metadata[i]
                            self.thread_report[int(i)]['len'] = metadata[i]

                    # Changes the number of threads according to the last download.
                    # This may be unwanted behavior in some cases, but hard to fix.
                    if len(self.thread_report) > 0:
                        logger.info('Resuming download.')
                        self.number_of_threads = len(self.thread_report)

                except json.JSONDecodeError:
                    logger.error('Failed reading from partfile.')


    def create_file(self):
        # Initializes a completely empty file for overwriting.
        if not os.path.isfile(self.path):
            with open(self.path, "wb") as file:
                # HACK!
                # By seeking and then writing you write a file full of zeroes without any issues.
                # On a 32 bit install doing self._total_size*b'0' can lead to overflowerrors.
                try:
                    file.seek(self._total_size-1)
                except OSError:
                    # Can happen on termux in some special directories.
                    raise OSError(f'Unable to write to {self.path}')
                file.write(b'0')


def set_range(start=0, end='', headers=None):
    if headers is None:
        headers = {}
    headers = copy.copy(headers)

    headers['Range'] = 'bytes={}-{}'.format(start, end)
    return headers
