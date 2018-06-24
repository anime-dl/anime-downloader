import requests
from bs4 import BeautifulSoup

import time
import os
import logging
import sys
import copy

from anime_downloader.sites.exceptions import AnimeDLError, NotFoundError
from anime_downloader.sites import util
from anime_downloader.const import desktop_headers


class BaseAnime:
    sitename = ''
    title = ''
    meta = dict()

    QUALITIES = None
    _episodeClass = object

    @classmethod
    def search(cls, query):
        return

    def __init__(self, url=None, quality='720p', _skip_online_data=False):
        self.url = url

        if quality in self.QUALITIES:
            self.quality = quality
        else:
            raise AnimeDLError('Quality {0} not found in {1}'.format(quality, self.QUALITIES))

        if not _skip_online_data:
            logging.info('Extracting episode info from page')
            self.get_data()

    @classmethod
    def verify_url(self, url):
        if self.sitename in url:
            return True
        return False

    def get_data(self):
        self._episodeIds = []
        r = requests.get(self.url, headers=desktop_headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        try:
            self._scrape_metadata(soup)
        except Exception as e:
            logging.debug(e)

        self._episodeIds = self._scarpe_episodes(soup)
        self._len = len(self._episodeIds)

        logging.debug('EPISODE IDS: length: {}, ids: {}'.format(
            self._len, self._episodeIds))

        self._episodeIds = [(no+1, id) for no, id in
                            enumerate(self._episodeIds)]

        return self._episodeIds

    def __len__(self):
        return self._len

    def __getitem__(self, index):
        if isinstance(index, int):
            ep_id = self._episodeIds[index]
            return self._episodeClass(ep_id[1], self.quality, parent=self,
                                      ep_no=ep_id[0])
        elif isinstance(index, slice):
            anime = copy.deepcopy(self)
            anime._episodeIds = anime._episodeIds[index]
            return anime

    def __repr__(self):
        return '''
Site: {name}
Anime: {title}
Episode count: {length}
'''.format(name=self.sitename, title=self.title, length=len(self))

    def __str__(self):
        return self.title

    def _scarpe_episodes(self, soup):
        return

    def _scrape_metadata(self, soup):
        return


class BaseEpisode:
    QUALITIES = None
    title = ''
    stream_url = ''

    def __init__(self, episode_id, quality='720p', parent=None,
                 ep_no=None):
        if quality not in self.QUALITIES:
            raise AnimeDLError('Incorrect quality: "{}"'.format(quality))

        self.ep_no = ep_no
        self.episode_id = episode_id
        self.quality = quality
        self._parent = parent
        self.pretty_title = '{}-{}'.format(self._parent.title, self.ep_no)

        logging.debug("Extracting stream info of id: {}".format(self.episode_id))

        try:
            self.get_data()
        except NotFoundError:
            parent.QUALITIES.remove(self.quality)
            for quality in parent.QUALITIES:
                logging.warning('Quality {} not found. Trying {}.'.format(self.quality, quality))
                self.quality = quality
                try:
                    self.get_data()
                    parent.quality = self.quality
                    break
                except NotFoundError:
                    parent.QUALITIES.remove(self.quality)

    def get_data(self):
        raise NotImplementedError

    def download(self, force=False, path=None,
                 format='{anime_title}_{ep_no}'):
        logging.info('Downloading {}'.format(self.pretty_title))
        if format:
            file_name = util.format_filename(format, self)+'.mp4'

        if path is None:
            path = './' + file_name
        if path.endswith('.mp4'):
            path = path
        else:
            path = os.path.join(path, file_name)

        logging.info(path)

        r = requests.get(self.stream_url, stream=True)

        util.make_dir(path.rsplit('/', 1)[0])

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

    def __repr__(self):
        return '<SearchResult Title: {} URL: {}>'.format(self.title, self.url)


def write_status(downloaded, total_size, start_time):
    elapsed_time = time.time()-start_time
    rate = (downloaded/1024)/elapsed_time if elapsed_time else 'x'
    downloaded = float(downloaded)/1048576
    total_size = float(total_size)/1048576

    status = 'Downloaded: {0:.2f}MB/{1:.2f}MB, Rate: {2:.2f}KB/s'.format(
        downloaded, total_size, rate)

    sys.stdout.write("\r" + status + " "*5 + "\r")
    sys.stdout.flush()
