from bs4 import BeautifulSoup

import os
import logging
import copy

from anime_downloader import session
from anime_downloader.sites.exceptions import AnimeDLError, NotFoundError
from anime_downloader import util
from anime_downloader.sites import helpers
from anime_downloader.const import desktop_headers
from anime_downloader.extractors import get_extractor
from anime_downloader.downloader import get_downloader


class Anime:
    sitename = ''
    title = ''
    meta = dict()
    subclasses = {}

    QUALITIES = None
    _episodeClass = object

    @classmethod
    def search(cls, query):
        return

    def __init__(self, url=None, quality='720p',
                 fallback_qualities=['720p', '480p', '360p'],
                 _skip_online_data=False):
        self.url = url
        self._fallback_qualities = fallback_qualities

        if quality in self.QUALITIES:
            self.quality = quality
        else:
            raise AnimeDLError(
                'Quality {0} not found in {1}'.format(quality, self.QUALITIES))

        if not _skip_online_data:
            logging.info('Extracting episode info from page')
            self.get_data()

    @classmethod
    def verify_url(self, url):
        if self.sitename in url:
            return True
        return False

    def __init_subclass__(cls, sitename, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses[sitename] = cls

    @classmethod
    def factory(cls, sitename: str):
        return cls.subclasses[sitename]

    def get_data(self):
        self._episode_urls = []
        try:
            self._scrape_metadata()
        except Exception as e:
            logging.debug('Metadata scraping error: {}'.format(e))

        self._episode_urls = self._scrape_episodes()
        self._len = len(self._episode_urls)

        logging.debug('EPISODE IDS: length: {}, ids: {}'.format(
            self._len, self._episode_urls))

        self._episode_urls = [(no+1, id) for no, id in
                              enumerate(self._episode_urls)]

        return self._episode_urls

    def __getitem__(self, index):
        episode_class = AnimeEpisode.subclasses[self.sitename]
        if isinstance(index, int):
            ep_id = self._episode_urls[index]
            return episode_class(ep_id[1], self.quality, parent=self,
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

    def __len__(self):
        return self._len

    def __str__(self):
        return self.title

    def _scrape_episodes(self):
        return

    def _scrape_metadata(self):
        return


class AnimeEpisode:
    QUALITIES = None
    title = ''
    stream_url = ''
    subclasses = {}

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
            qualities = copy.copy(self._parent._fallback_qualities)
            try:
                qualities.remove(self.quality)
            except ValueError:
                pass
            for quality in qualities:
                logging.warning('Quality {} not found. Trying {}.'.format(
                    self.quality, quality))
                self.quality = quality
                try:
                    self.get_data()
                    self.source().stream_url
                    # parent.quality = self.quality
                    break
                except NotFoundError:
                    # Issue #28
                    # qualities.remove(self.quality)
                    pass

    def __init_subclass__(cls, sitename: str, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses[sitename] = cls
        cls.sitename = sitename

    @classmethod
    def factory(cls, sitename: str):
        return cls.subclasses[sitename]

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
        logging.debug('Sources : '.format(self._sources))

    def _get_sources(self):
        raise NotImplementedError

    def download(self, force=False, path=None,
                 format='{anime_title}_{ep_no}', range_size=None):
        # TODO: Remove this shit
        logging.info('Downloading {}'.format(self.pretty_title))
        if format:
            file_name = util.format_filename(format, self)+'.mp4'

        if path is None:
            path = './' + file_name
        if path.endswith('.mp4'):
            path = path
        else:
            path = os.path.join(path, file_name)

        Downloader = get_downloader('http')
        downloader = Downloader(self.source(),
                                path, force, range_size=range_size)

        downloader.download()


class SearchResult:
    def __init__(self, title, url, poster):
        self.title = title
        self.url = url
        self.poster = poster
        self.meta = ''

    def __repr__(self):
        return '<SearchResult Title: {} URL: {}>'.format(self.title, self.url)

    def __str__(self):
        return self.title
