import requests
from bs4 import BeautifulSoup

import time
import os
import logging
import sys
import copy
from pget import down
import shutil

from anime_downloader.sites.exceptions import AnimeDLError, NotFoundError
from anime_downloader import util
from anime_downloader.const import desktop_headers
from anime_downloader.extractors import get_extractor


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
        self._episode_urls = []
        r = requests.get(self.url, headers=desktop_headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        try:
            self._scrape_metadata(soup)
        except Exception as e:
            logging.debug('Metadata scraping error: {}'.format(e))

        self._episode_urls = self._scarpe_episodes(soup)
        self._len = len(self._episode_urls)

        logging.debug('EPISODE IDS: length: {}, ids: {}'.format(
            self._len, self._episode_urls))

        self._episode_urls = [(no+1, id) for no, id in
                            enumerate(self._episode_urls)]

        return self._episode_urls

    def __len__(self):
        return self._len

    def __getitem__(self, index):
        if isinstance(index, int):
            ep_id = self._episode_urls[index]
            return self._episodeClass(ep_id[1], self.quality, parent=self,
                                      ep_no=ep_id[0])
        elif isinstance(index, slice):
            anime = copy.deepcopy(self)
            anime._episode_urls = anime._episode_urls[index]
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

    def __init__(self, url, quality='720p', parent=None,
                 ep_no=None):
        if quality not in self.QUALITIES:
            raise AnimeDLError('Incorrect quality: "{}"'.format(quality))

        self.ep_no = ep_no
        self.url = url
        self.quality = quality
        self._parent = parent
        self._sources = None
        self.pretty_title = '{}-{}'.format(self._parent.title, self.ep_no)

        logging.debug("Extracting stream info of id: {}".format(self.url))

        # TODO: New flag: online_data=False
        try:
            self.get_data()
            # Just to verify the source is acquired
            self.source().stream_url
        except NotFoundError:
            # Issue #28
            qualities = self.QUALITIES
            qualities.remove(self.quality)
            for quality in qualities:
                logging.warning('Quality {} not found. Trying {}.'.format(self.quality, quality))
                self.quality = quality
                try:
                    self.get_data()
                    self.source().stream_url
                    # parent.quality = self.quality
                    break
                except NotFoundError:
                    # Issue #28
                    qualities.remove(self.quality)
                    pass

    def source(self, index=0):
        if not self._sources:
            self.get_data()

        try:
            sitename, url = self._sources[index]
        except TypeError:
            return self._sources[index]

        extractor = get_extractor(sitename)
        ext = extractor(url, quality=self.quality)
        self._sources[index] = ext

        return ext

    def get_data(self):
        self._sources = self._get_sources()

    def _get_sources(self):
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

        r = requests.get(self.source().stream_url, stream=True)

        util.make_dir(path.rsplit('/', 1)[0])

        try:
            total_size = int(r.headers['Content-length'])
        except KeyError:
            logging.warning('m3u8 downloading not supported yet')
            return
        downloaded, chunksize = 0, 16384
        start_time = time.time()

        if os.path.exists(path):
            if os.stat(path).st_size == total_size and not force:
                logging.warning('File already downloaded. Skipping download.')
                return
            else:
                os.remove(path)

        # if r.status_code == 200:
        #     with open(path, 'wb') as f:
        #         for chunk in r.iter_content(chunk_size=chunksize):
        #             if chunk:
        #                 f.write(chunk)
        #                 downloaded += chunksize
        #                 write_status((downloaded), (total_size),
        #                              start_time)
        # return

        downloader = down.Downloader(self.source().stream_url, path, 16)
        downloader.start()

        def callback(d):
            rate = d.readable_speed
            downloaded = float(d.total_downloaded)/1048576
            total_size = float(d.total_length)/1048576
            status_to_stdout(downloaded, total_size, rate)

        downloader.subscribe(download_callback, 256)
        try:
            downloader.wait_for_finish()
        except KeyboardInterrupt:
            downloader.stop()
            raise


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
    status_to_stdout(downloaded, total_size, str(rate)+'KB/s')


def status_to_stdout(downloaded, total_size, rate):
    status = 'Downloaded: {0:.2f}MB/{1:.2f}MB, Rate: {2}'.format(
        downloaded, total_size, rate)

    sys.stdout.write("\r" + status + " "*5 + "\r")
    sys.stdout.flush()


def download_callback(downloader):
    term_width, term_height = shutil.get_terminal_size()
    if term_width >= 100:
        term_width = 100

    if downloader.get_state() == down.Downloader.DOWNLOADING:
        written_update = "[{:3}%] [{}/sec]"
        percent_downloaded = int(100 * (float(downloader.total_downloaded) / downloader.total_length))
        written_update = written_update.format(
            percent_downloaded,
            downloader.readable_speed
        )

        if len(written_update) < term_width * 3 / 4:
            fill_in_area = term_width - (len(written_update) + 3)
            done = int(fill_in_area * percent_downloaded / 100) * '='
            remaining = (fill_in_area - len(done)) * ' '
            written_update += ' [{}{}]'.format(done, remaining)
        else:
            written_update += (' ' * (term_width - len(written_update)))

        if downloader.total_downloaded == downloader.total_length:
            written_update += '\n'

        sys.stdout.write('\r' + written_update)
        sys.stdout.flush()
    elif downloader.get_state() == down.Downloader.MERGING:
        written_update = "[Merging {:5}/{:5}]".format(down.readable_bytes(downloader.total_merged),
                                                      down.readable_bytes(downloader.total_length))
        if len(written_update) < term_width * 3 / 4:
            fill_in_area = term_width - (len(written_update) + 3)
            done = int((downloader.total_merged * fill_in_area) / downloader.total_length) * '='
            remaining = (fill_in_area - len(done)) * ' '
            written_update += ' [{}{}]'.format(done, remaining)
        else:
            written_update += (' ' * (term_width - len(written_update)))

        if downloader.total_merged == downloader.total_length:
            written_update += '\n'

        sys.stdout.write('\r' + written_update)
        sys.stdout.flush()
