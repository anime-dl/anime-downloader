from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import json
import re
import logging

logger = logging.getLogger(__name__)


class AniMixPlay(Anime, sitename='dubbedanime'):
    sitename='animixplay'
    @classmethod
    def search(cls, query):
        search_results = helpers.soupify(helpers.get('https://animixplay.com/', params = {"q" : query})).select('p.name > a')
        search_results = [
            SearchResult(
                title = a.text,
                url = 'https://animixplay.com' + a.get('href')
            )
            for a in search_results
        ]
        return(search_results)

    def _scrape_episodes(self):
        """
        _scrape_episodes is function which has to be overridden by the base
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

class AniMixPlayEpisode(AnimeEpisode, sitename='dubbedanime'):
    def _get_sources(self):
        raise NotImplementedError
