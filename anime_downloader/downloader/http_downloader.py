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
        url = self.source.stream_url
        headers = self.source.headers

        # Defaults headers if not specified.
        if 'user-agent' not in headers:
            headers['user-agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101Firefox/56.0",

        if self.source.referer:
            headers['Referer'] = self.source.referer

        # Can be defined in config.
        # NOTE: Dont assume it'll always be this number.
        # It'll revert to 1 thread under certain circumstances.
        self.number_of_threads = 8

        # Some downloads can have an unknown size. 
        # This makes the downloader use 1 thread for safety.
        if not self._total_size:
            logger.info('Unknown file size. Using 1 thread.')

        # Init a process manager
        manager = mp.Manager()
        q = manager.Queue()
        pool = mp.Pool(mp.cpu_count() + 2)

        self.thread_report = manager.list()
        # This makes number_of_threads 1 if the file is small enough or unknown.
        self.number_of_threads = self.number_of_threads if self._total_size > self.chunksize*self.number_of_threads else 1

        # If downloaded file is file.mp4 the partfile will be file.part
        # NOTE: This may cause issues the the file path includes a "." and not the file.
        partfile = "".join(os.path.abspath(self.path).split('.')[:-1])+'.part'
        # If there's already a partfile it tries to read it to continue the download.
        # The amout of if statements is to make it safe even if the partfile is corrupted/from another program.
        if os.path.isfile(partfile):
            with open(partfile,"r") as metadata:
                try:
                    metadata = json.load(metadata)
                    for i in metadata:
                        if i.isnumeric() and type(metadata[i]) is int:
                            # Creates a "thread safe" dict.
                            if not len(self.thread_report) > int(i):
                                self.thread_report.append(manager.dict())

                            # Adds to the downloaded (to make the progress show up properly).
                            self.downloaded += metadata[i]
                            self.thread_report[int(i)]['len'] = metadata[i]

                    # Changes the number of threads according to the last download.
                    # This may be unwanted behavior in some cases, but hard to fix.
                    if len(self.thread_report) > 0:
                        logger.info('Resuming download.')
                        self.number_of_threads = len(self.thread_report)

                except json.JSONDecodeError:
                    logger.error('Failed reading from partfile.')

        # Initializes a completely empty file for overwriting.
        if not os.path.isfile(self.path):
            with open(self.path, "wb") as file:
                # HACK!
                # By seeking and then writing you write a file full of zeroes without any issues.
                # On a 32 bit install doing self._total_size*b'0' can lead to overflowerrors.
                file.seek(self._total_size-1)
                file.write(b'0')

        # By this time self.number_of_threads should not be changed.
        logger.info('Using {} thread{}.'.format(self.number_of_threads, (self.number_of_threads > 1) *'s'))
        # Divides the download into parts, used for offset in writing the file.
        self.part = math.floor(self._total_size / self.number_of_threads)

        # To get reliable feedback from the threads it uses a dict containing the thread states.
        # This allows maximum download and resumption if any of the threads fail halfway.
        # Prepares the threads with starting info.

        """
        self.thread_report is a dict accesible from all threads used transfer info between them.
        This CAN be removed in favor of reading from the partfile when necessary which can reduce code 
        complexity at the cost of flexibility.

        self.thread_report has a layout of:
        [{'len': 1687552, 'start': 0, 'end': 23609903, 'done': False},
         {'len': 671744, 'start': 23609904, 'end': 47219807, 'done': False}]

        Where each element of the list is a dict containing info on the thread.
        'len' is the actual length of all the chunks combined used for offsets when writing.
        NOTE: len != self.chunksize*chunks as a chunk can for example be 9 byes when the chunksize is 8.
        This 'issue' is unavoidable as far as I know.
        'start' is where the download should start, used for requests.
        'end' is where the download should end, also used for requests.
        'done' is a bool if the download is complete.
        """
        for i in range(self.number_of_threads):
            if not len(self.thread_report) > i:
                self.thread_report.append(manager.dict())

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

        jobs = []

        logger.info('Starting download.')
        # NOTE: starting the time MUST be done before starting the consumer or else it'll error.
        # The consumer uses the start time to print download progress and will (silently) error without it.
        self.start_time = time.time()

        # Starts a consumer which writes to the file.
        # Writing to the same file from multiple places isn't very reliable.
        consumer = pool.apply_async(self.consumer, (q,))

        # Arbitrary max tries, somewhat high number.
        # This resumes the download if one of the threads fail (for example due to cap on connections).
        for attempt in range(self.number_of_threads*2):
            for i in range(self.number_of_threads):
                # If the thread is done it'll do nothing.
                # Eventually ending in only one thread downloading.
                # Always having max threads downloading would be too complex.
                if self.thread_report[i].get('done'):
                    continue

                # Start gets offset based on the previous downloaded chunks.
                start = self.thread_report[i]['start']
                start += self.thread_report[i]['len']

                end = self.thread_report[i]['end']
                # Just in case, creating tons of threads at once seems to cause issues.
                time.sleep(0.2)
                # Starts the thread downloader.
                job = pool.apply_async(self.thread_downloader, (url, start, end, headers, i, q,))
                jobs.append(job)

            for job in jobs:
                job.get()

        # Kill the consumer.
        q.put('kill')
        pool.close()
        pool.join()
        # Cleans up the partfile on completed download.
        if os.path.isfile(partfile):
            os.remove(partfile)

    def thread_downloader(self, url, start, end, headers, number, q):
        if end:
            headers['Range'] = 'bytes=%d-%d' % (start, end)

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


    def consumer(self, q):
        # ANY ERRORS HERE ARE SILENT.
        # If there's an error in this function nothing will happen besides that the 
        # download progress won't go up.

        """Listen to consumer queue and write file using offset
        :param q: Consumer queue
        """
        # Opening the file as r+b is absolutely essential to continuing downloads without corrupting them.
        f = open(self.path, 'r+b')
        partfile = "".join(os.path.abspath(self.path).split('.')[:-1])+'.part'
        metadata = open(partfile, "w+")
        metadata.write('{}')

        # Meta is a duplicate of self.thread_report, but only includes len
        # You might think that It'd be better to just write from self.thread_report
        # but that causes a severe bottleneck (and errors it seems) compared to keeping an internal state.
        meta = {}
        # Meta looks like {0:1234, 1:100, 2:0}
        # where the key is the thread number and the value is length written.
        for i in range(self.number_of_threads):
            meta[i] = 0

        while True:
            message = q.get()
            if message is 'kill':
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
                # Reports the the chunk is actually downloaded, causing an uptick in the progress bar.
                self.report_chunk_downloaded(len(chunk))
                # Makes sure the data is written directly.
                f.flush()

        f.close()
        metadata.close()


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
                        self.report_chunk_downloaded(len(chunk))


def set_range(start=0, end='', headers=None):
    if headers is None:
        headers = {}
    headers = copy.copy(headers)

    headers['Range'] = 'bytes={}-{}'.format(start, end)
    return headers
