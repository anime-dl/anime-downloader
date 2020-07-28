"""
anime.py contains the base classes required for other anime classes.
"""
import os
import logging
import copy
import importlib

from anime_downloader.sites.exceptions import AnimeDLError, NotFoundError
from anime_downloader import util
from anime_downloader.config import Config
from anime_downloader.extractors import get_extractor
from anime_downloader.downloader import get_downloader

logger = logging.getLogger(__name__)


class Anime:
    """
    Base class for all anime classes.

    Parameters
    ----------
    url: string
        URL of the anime.
    quality: One of ['360p', '480p', '720p', '1080p']
        Quality of episodes
    fallback_qualities: list
        The order of fallback.

    Attributes
    ----------
    sitename: str
        name of the site
    title: str
        Title of the anime
    meta: dict
        metadata about the anime. [Can be empty]
    QUALITIES: list
        Possible qualities for the site
    """
    sitename = ''
    title = ''
    meta = dict()
    subclasses = {}
    QUALITIES = ['360p', '480p', '720p', '1080p']

    @classmethod
    def search(cls, query):
        """
        Search searches for the anime using the query given.

        Parameters
        ----------
        query: str
            query is the query keyword to be searched.

        Returns
        -------
        list
            List of :py:class:`~anime_downloader.sites.anime.SearchResult`
        """
        return

    def __init__(self, url=None, quality='720p',
                 fallback_qualities=None,
                 _skip_online_data=False):
        self.url = url

        if fallback_qualities is None:
            fallback_qualities = ['720p', '480p', '360p']

        self._fallback_qualities = [
            q for q in fallback_qualities if q in self.QUALITIES]

        if quality in self.QUALITIES:
            self.quality = quality
        else:
            raise AnimeDLError(
                'Quality {0} not found in {1}'.format(quality, self.QUALITIES))

        if not _skip_online_data:
            logger.info('Extracting episode info from page')
            self._episode_urls = self.get_data()
            self._len = len(self._episode_urls)

    @classmethod
    def verify_url(cls, url):
        if cls.sitename in url:
            return True
        return False

    @property
    def config(self):
        return Config['siteconfig'][self.sitename]

    def __init_subclass__(cls, sitename, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses[sitename] = cls

    @classmethod
    def factory(cls, sitename: str):
        """
        factory returns the appropriate subclass for the given site name.

        Parameters
        ----------
        sitename: str
            sitename is the name of the site

        Returns
        -------
        subclass of :py:class:`Anime`
            Sub class of :py:class:`Anime`
        """
        return cls.subclasses[sitename]

    @classmethod
    def new_anime(cls, sitename: str):
        """
        new_anime is a factory which returns the anime class corresposing to
        `sitename`

        Returns
        -------
        subclass of Anime
        """
        module = importlib.import_module(
            'anime_downloader.sites.{}'.format(sitename)
        )
        for c in dir(module):
            if issubclass(c, cls):
                return c
        raise ImportError("Cannot find subclass of {}".format(cls))

    def get_data(self):
        """
        get_data is called inside the :code:`__init__` of
        :py:class:`~anime_downloader.sites.anime.BaseAnime`. It is used to get
        the necessary data about the anime and it's episodes.

        This function calls
        :py:class:`~anime_downloader.sites.anime.BaseAnime._scarpe_episodes`
        and
        :py:class:`~anime_downloader.sites.anime.BaseAnime._scrape_metadata`

        TODO: Refactor this so that classes which need not be soupified don't
        have to overload this function.

        Returns
        -------
        list
            A list of tuples of episodes containing episode name and
            episode url.
            Ex::
                [('1', 'https://9anime.is/.../...', ...)]

        """
        self._episode_urls = []
        try:
            self._scrape_metadata()
        except Exception as e:
            logger.debug('Metadata scraping error: {}'.format(e))

        self._episode_urls = self._scrape_episodes()
        self._len = len(self._episode_urls)

        logger.debug('EPISODE IDS: length: {}, ids: {}'.format(
            self._len, self._episode_urls))

        if not isinstance(self._episode_urls[0], tuple):
            self._episode_urls = [(no+1, id) for no, id in
                                enumerate(self._episode_urls)]

        return self._episode_urls

    def __getitem__(self, index):
        episode_class = AnimeEpisode.subclasses[self.sitename]
        if isinstance(index, int):
            try:
                ep_id = self._episode_urls[index]
            except IndexError as e:
                raise RuntimeError("No episode found with index") from e
            return episode_class(ep_id[1], parent=self,
                                 ep_no=ep_id[0])
        elif isinstance(index, slice):
            anime = copy.deepcopy(self)
            try:
                anime._episode_urls = anime._episode_urls[index]
            except IndexError as e:
                raise RuntimeError("No episode found with index") from e
            return anime
        return None

    def __iter__(self):
        episode_class = AnimeEpisode.subclasses[self.sitename]
        for ep_id in self._episode_urls:
            yield episode_class(ep_id[1], parent=self, ep_no=ep_id[0])

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

    def _scarpe_episodes(self):
        """
        _scarpe_episodes is function which has to be overridden by the base
        classes to scrape the episode urls from the web page.

        Parameters
        ----------
        soup: `bs4.BeautifulSoup`
            soup is the html of the anime url after passing through
            BeautifulSoup.

        Returns
        -------
        :code:`list` of :code:`str`
            A list of episode urls.
        """
        return

    def _scrape_metadata(self):
        """
        _scrape_metadata is function which has to be overridden by the base
        classes to scrape the metadata of anime from the web page.

        Parameters
        ----------
        soup: :py:class:`bs4.BeautifulSoup`
            soup is the html of the anime url after passing through
            BeautifulSoup.
        """
        return


class AnimeEpisode:
    """
    Base class for all Episode classes.

    Parameters
    ----------
    url: string
        URL of the episode.
    quality: One of ['360p', '480p', '720p', '1080p']
        Quality of episode
    fallback_qualities: list
        The order of fallback.

    Attributes
    ----------
    sitename: str
        name of the site
    title: str
        Title of the anime
    meta: dict
        metadata about the anime. [Can be empty]
    ep_no: string
        Episode number/title of the episode
    pretty_title: string
        Pretty title of episode in format <animename>-<ep_no>
    """
    QUALITIES = []
    title = ''
    stream_url = ''
    subclasses = {}

    def __init__(self, url, parent: Anime = None, ep_no=None):

        self.ep_no = ep_no
        self.url = url
        self.quality = parent.quality
        self.QUALITIES = parent.QUALITIES
        self._parent = parent
        self._sources = None
        self.pretty_title = '{}-{}'.format(self._parent.title, self.ep_no)

        logger.debug("Extracting stream info of id: {}".format(self.url))

        def try_data():
            self.get_data()
            # Just to verify the source is acquired
            self.source().stream_url
        try:
            try_data()
        except NotFoundError:
            # Issue #28
            qualities = copy.copy(self._parent._fallback_qualities)
            try:
                qualities.remove(self.quality)
            except ValueError:
                pass
            for quality in qualities:
                logger.warning('Quality {} not found. Trying {}.'.format(
                    self.quality, quality))
                self.quality = quality
                try:
                    try_data()
                    return
                except NotFoundError:
                    pass
            logger.warning(f'Skipping episode: {self.ep_no}')

    def __init_subclass__(cls, sitename: str, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses[sitename] = cls
        cls.sitename = sitename

    @classmethod
    def factory(cls, sitename: str):
        return cls.subclasses[sitename]

    @property
    def config(self):
        return Config['siteconfig'][self.sitename]

    def source(self, index=0):
        """
        Get the source for episode

        Returns
        -------
        `anime_downloader.extractors.base_extractor.BaseExtractor`
            Extractor depending on the source.
        """
        if not self._sources:
            self.get_data()
        try:
            sitename, url = self._sources[index]
        except TypeError:
            return self._sources[index]
        except IndexError:
            raise NotFoundError("No episode sources found.")

        ext = get_extractor(sitename)(url, quality=self.quality)
        self._sources[index] = ext

        return ext

    def get_data(self):
        self._sources = self._get_sources()
        logger.debug('Sources : {}'.format(self._sources))

    def _get_sources(self):
        raise NotImplementedError


    def sort_sources(self, data):
        """
        Formatted data should look something like this
        
        [
        {'extractor': 'mp4upload', 'url': 'https://twist.moe/mp4upload/...', 'server': 'mp4upload', 'version': 'subbed'}, 
        {'extractor': 'vidstream', 'url': 'https://twist.moe/vidstream/...', 'server': 'vidstream', 'version': 'dubbed'},
        {'extractor': 'no_extractor', 'url': 'https://twist.moe/anime/...', 'server': 'default', 'version': 'subbed'}
        ]

        extractor = the extractor the link should be passed to
        url = url to be passed to the extractor
        server = the server name used in config
        version = subbed/dubbed

        The config should consist of a list with servers in preferred order and a preferred language, eg
        
        "servers":["vidstream","default","mp4upload"],
        "version":"subbed"

        Using the example above, this function will return: [('no_extractor', 'https://twist.moe/anime/...')]
        as it prioritizes preferred language over preferred server
        """

        version = self.config.get('version','subbed') #TODO add a flag for this
        servers = self.config.get('servers',[''])

        logger.debug('Data : {}'.format(data))

        #Sorts the dicts by preferred server in config
        sorted_by_server = sorted(data, key=lambda x: servers.index(x['server']) if x['server'] in servers else len(data))

        #Sorts the above by preferred language 
        #resulting in a list with the dicts sorted by language and server
        #with language being prioritized over server
        sorted_by_lang = list(sorted(sorted_by_server, key=lambda x: x['version'] == version, reverse=True))
        logger.debug('Sorted sources : {}'.format(sorted_by_lang))

        return '' if not sorted_by_lang else [(sorted_by_lang[0]['extractor'],sorted_by_lang[0]['url'])]


    def download(self, force=False, path=None,
                 format='{anime_title}_{ep_no}', range_size=None):
        """
        Downloads episode. This might be removed in a future release.

        Parameters
        ----------
        force: bool
            Whether to force download or not.
        path: string
            Path to the directory/file where the file should be downloaded to.
        format: string
            The format of the filename if not provided.
        """
        # TODO: Remove this shit
        logger.info('Downloading {}'.format(self.pretty_title))
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
    """
    SearchResult class holds the search result of a search done by an Anime
    class

    Parameters
    ----------
    title: str
        Title of the anime.
    url: str
        URL of the anime
    poster: str
        URL for the poster of the anime.
    meta: dict
        Additional metadata regarding the anime.

    Attributes
    ----------
    title: str
        Title of the anime.
    url: str
        URL of the anime
    poster: str
        URL for the poster of the anime.
    meta: dict
        Additional metadata regarding the anime.
    """

    def __init__(self, title, url, poster='', meta=''):
        self.title = title
        self.url = url
        self.poster = poster
        self.meta = meta

    def __repr__(self):
        return '<SearchResult Title: {} URL: {}>'.format(self.title, self.url)

    def __str__(self):
        return self.title

    @property
    def pretty_metadata(self):
        """
        pretty_metadata is the prettified version of metadata
        """
        if self.meta:
            return ' | '.join(val for _, val in self.meta.items())
        return ''
