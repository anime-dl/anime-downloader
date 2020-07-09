from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import json
import re
import logging

logger = logging.getLogger(__name__)

class AniMixPlay(Anime, sitename='animixplay'):
    sitename='animixplay'
    @classmethod
    def search(cls, query):
        jsonVar = helpers.post("https://animixplay.com/api/search", data = {"qfast": query}, verify = False).json()
        soup = helpers.soupify(jsonVar["result"]).select('div.details a:not([href*=v2]):not([href*=v4])')
        logger.debug(soup)
        search_results = [
            SearchResult(
                title = a.text,
                url = 'https://animixplay.com' + a.get('href')
            )
            for a in soup
        ]
        return(search_results)

    def _scrape_episodes(self):
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