import requests
from bs4 import BeautifulSoup
import json
import re

import time
import os
import click
import logging

from anime_downloader.sites.exceptions import AnimeDLError, NotFoundError
from anime_downloader import util


class BaseAnime():
    sitename = ''
    title = ''

    QUALITIES = None
    _episodeClass = object

    def __init__(self, url, quality='720p'):

        if quality not in self.QUALITIES:
            raise AnimeDLError('Incorrect quality: "{}"'.format(quality))

        self.url = self.verify_url(url)

        if quality in self.QUALITIES:
            self.quality = quality
        else:
            raise AnimeDLError('Quality {0} not found in {1}'.format(quality, self.QUALITIES))

        logging.info('Extracting episode info from page')
        self.getEpisodes()

    def verify_url(self, url):
        return url

    def getEpisodes(self):
        self._episodeIds = []
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        self._soup = soup

        self._getMetadata(soup)

        self._episodeIds = self._getEpisodeUrls(soup)
        self._len = len(self._episodeIds)

        logging.debug('EPISODE IDS: length: {}, ids: {}'.format(
            self._len, self._episodeIds))

        return self._episodeIds

    def __len__(self):
        return self._len

    def __getitem__(self, index):
        ep_id = self._episodeIds[index]
        return self._episodeClass(ep_id, self.quality, parent=self)

    def __repr__(self):
        return '''
Site: {name}
Anime: {title}
Episode count: {length}
'''.format(name=self.sitename, title=self.title, length=len(self))

    def _getEpisodeUrls(self, soup):
        return

    def _getMetadata(self, soup):
        return

class BaseEpisode:
    QUALITIES = None
    title = ''
    stream_url = ''

    def __init__(self, episode_id, quality='720p', parent=None):

        if quality not in self.QUALITIES:
            raise AnimeDLError('Incorrect quality: "{}"'.format(quality))

        self.episode_id = episode_id
        self.quality = quality
        logging.info("Extracting stream info of id: {}".format(self.episode_id))

        try:
            self.getData()
        except NotFoundError:
            for quality in parent.QUALITIES:
                parent.QUALITIES.remove(self.quality)
                logging.warning('Quality {} not found. Trying {}.'.format(self.quality, quality))
                self.quality = quality
                try:
                    self.getData()
                    parent.quality = self.quality
                    break
                except NotFoundError:
                    pass

    def getData(self):
        raise NotImplementedError

    def download(self, force=False, path=None):
        logging.info('Downloading {}'.format(self.title))

        if path is None:
            path = './' + self.title
        elif path.endswith('.mp4'):
            path = path
        else:
            path += self.title

        r = requests.get(self.stream_url, stream=True)

        total_size = int(r.headers['Content-length'])
        downloaded, chunksize = 0, 16384
        start_time = time.time()

        logging.debug(path)

        if os.path.exists(path):
            if os.stat(path).st_size == total_size and not force:
                logging.warning('File already downloaded. Skipping download.')
                return
            else:
                os.remove(path)

        if r.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=chunksize):
                    if chunk:
                        f.write(chunk)
                        downloaded += chunksize
                        util.write_status((downloaded), (total_size),
                                          start_time)
