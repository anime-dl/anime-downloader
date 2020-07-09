from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import json
import re
import logging

logger = logging.getLogger(__name__)

<<<<<<< HEAD

class AniMixPlay(Anime, sitename='dubbedanime'):
    sitename='animixplay'
    @classmethod
    def search(cls, query):
        search_results = helpers.soupify(helpers.get('https://animixplay.com/', params = {"q" : query})).select('p.name > a')
=======
class AniMixPlay(Anime, sitename='animixplay'):
    sitename='animixplay'
    @classmethod
    def search(cls, query):
        jsonVar = helpers.post("https://animixplay.com/api/search", data = {"qfast": query}, verify = False).json()
        soup = helpers.soupify(jsonVar["result"]).select('div.details a:not([href*=v2]):not([href*=v4])')
        logger.debug(soup)
>>>>>>> Patch-2
        search_results = [
            SearchResult(
                title = a.text,
                url = 'https://animixplay.com' + a.get('href')
            )
<<<<<<< HEAD
            for a in search_results
=======
            for a in soup
>>>>>>> Patch-2
        ]
        return(search_results)

    def _scrape_episodes(self):
<<<<<<< HEAD
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
=======
        url = self.url
        soup = helpers.soupify(helpers.get(url))
        ep_list = soup.find('div', {'id':'epslistplace'})
        logger.debug(ep_list.get_text())
        jdata = json.loads(ep_list.get_text())
        keyList = list(jdata.keys())
        del keyList[0]
        logger.debug(keyList)
        return [jdata[x] for x in keyList]

class AniMixPlayEpisode(AnimeEpisode, sitename='animixplay'):
    def _get_sources(self):
        logger.debug(self.url)
        return [('vidstream', self.url)]
>>>>>>> Patch-2
