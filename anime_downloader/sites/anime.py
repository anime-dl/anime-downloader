import requests
from bs4 import BeautifulSoup

import time
import os
import logging
import sys

from anime_downloader.sites.exceptions import AnimeDLError, NotFoundError


class BaseAnime:
    sitename = ''
    title = ''
    meta = dict()

    QUALITIES = None
    _episodeClass = object

    @classmethod
    def search(cls, query):
        return

    def __init__(self, url, quality='720p', path=None):
        self.url = url
        self.path = path

        if path:
            logging.info('Downloading to {}'.format(os.path.abspath(path)))

        if quality in self.QUALITIES:
            self.quality = quality
        else:
            raise AnimeDLError('Quality {0} not found in {1}'.format(quality, self.QUALITIES))

        logging.info('Extracting episode info from page')
        self.getEpisodes()

    @classmethod
    def verify_url(self, url):
        if self.sitename in url:
            return True
        return False

    def getEpisodes(self):
        self._episodeIds = []
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')

        try:
            self._getMetadata(soup)
        except Exception as e:
            logging.debug(e)

        self._episodeIds = self._getEpisodeUrls(soup)
        self._len = len(self._episodeIds)

        logging.debug('EPISODE IDS: length: {}, ids: {}'.format(
            self._len, self._episodeIds))

        return self._episodeIds

    def __len__(self):
        return self._len

    def __getitem__(self, index):
        if isinstance(index, int):
            ep_id = self._episodeIds[index]
            return self._episodeClass(ep_id, self.quality, parent=self,
                                      path=self.path, ep_no=index+1)
        elif isinstance(index, slice):
            self._episodeIds = self._episodeIds[index]
            return self

    def __repr__(self):
        return '''
Site: {name}
Anime: {title}
Episode count: {length}
'''.format(name=self.sitename, title=self.title, length=len(self))

    def __str__(self):
        return self.title

    def _getEpisodeUrls(self, soup):
        return

    def _getMetadata(self, soup):
        return


class BaseEpisode:
    QUALITIES = None
    title = ''
    stream_url = ''

    def __init__(self, episode_id, quality='720p', parent=None, path=None,
                 ep_no=None):

        self.path = path

        if quality not in self.QUALITIES:
            raise AnimeDLError('Incorrect quality: "{}"'.format(quality))

        self.episode_id = episode_id
        self.quality = quality
        logging.debug("Extracting stream info of id: {}".format(self.episode_id))

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
            if self.path is None:
                path = './' + self.title
            else:
                path = self.path
        if path.endswith('.mp4'):
            path = path
        else:
            path = os.path.join(path, self.title)

        logging.info(path)

        r = requests.get(self.stream_url, stream=True)

        total_size = int(r.headers['Content-length'])
        downloaded, chunksize = 0, 16384
        start_time = time.time()

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
                        write_status((downloaded), (total_size),
                                      start_time)


class SearchResult:
    def __init__(self, title, url, poster):
        self.title = title
        self.url = url
        self.poster = poster
        self.meta = ''


def write_status(downloaded, total_size, start_time):
    elapsed_time = time.time()-start_time
    rate = (downloaded/1024)/elapsed_time
    downloaded = float(downloaded)/1048576
    total_size = float(total_size)/1048576

    status = 'Downloaded: {0:.2f}MB/{1:.2f}MB, Rate: {2:.2f}KB/s'.format(
        downloaded, total_size, rate)

    sys.stdout.write("\r" + status + " "*5 + "\r")
    sys.stdout.flush()
