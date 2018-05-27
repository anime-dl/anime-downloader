import requests
from bs4 import BeautifulSoup
import json
import re

import time
import sys
import os
import click
import logging

from .exceptions import AnimeDLError


class BaseAnime():
    QUALITIES = None
    _episodeClass = None

    def __init__(self, url, quality='720p'):

        if quality not in self.QUALITIES:
            raise AnimeDLError('Incorrect quality: "{}"'.format(quality))

        self.url = self.verify_url(url)

        if quality in self.QUALITIES:
            self.quality = quality
        else:
            raise AnimeDLError(f'Quality {quality} not found in {self.QUALITIES}')

        logging.info('Extracting episode info from page')
        self.getEpisodes()

    def verify_url(self, url):
        return url

    def getEpisodes(self):
        self._episodeIds = []
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        return self._getEpisodeUrls(soup)

    def __len__(self):
        return len(self._episodeIds)

    def __getitem__(self, index):
        ep_id = self._episodeIds[index]
        return self._episodeClass(ep_id, self.quality)

    def _getEpisodeUrls(self, soup):
        return


class BaseEpisode:
    QUALITIES = None
    title = ''
    stream_url = ''

    def __init__(self, episode_id, quality='720p'):

        if quality not in self.QUALITIES:
            raise AnimeDLError('Incorrect quality: "{}"'.format(quality))

        self.episode_id = episode_id
        self.quality = quality
        logging.info("Extracting stream info of id: {}".format(self.episode_id))
        self.getData()

    def getData(self):
        raise NotImplementedError

    def download(self, force=False):
        logging.info('Downloading {}'.format(self.title))
        path = './' + self.title
        r = requests.get(self.stream_url, stream=True)

        total_size = int(r.headers['Content-length'])
        downloaded, chunksize = 0, 16384
        start_time = time.time()

        if os.path.exists(path) and not force:
            if os.stat(path).st_size == total_size:
                logging.warning('File already downloaded. Skipping download.')
                return

        if r.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=chunksize):
                    if chunk:
                        f.write(chunk)
                        downloaded += chunksize
                        write_status((downloaded), (total_size),
                                        start_time)


def write_status(downloaded, total_size, start_time):
    elapsed_time = time.time()-start_time
    rate = (downloaded/1024)/elapsed_time
    downloaded = float(downloaded)/1048576
    total_size = float(total_size)/1048576

    status = 'Downloaded: {0:.2f}MB/{1:.2f}MB, Rate: {2:.2f}KB/s'.format(
        downloaded, total_size, rate)

    sys.stdout.write("\r" + status + " "*5 + "\r")
    sys.stdout.flush()
