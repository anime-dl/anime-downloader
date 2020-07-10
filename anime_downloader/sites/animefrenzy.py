from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import json
import re
import logging

logger = logging.getLogger(__name__)

class AnimeFrenzy(Anime, sitename='animefrenzy'):
    sitename='animefrenzy'
    @classmethod
    def search(cls, query):
        r = helpers.get("https://animefrenzy.net/search", params = {"q": query})
        soup = helpers.soupify(r)
        titleName = soup.select("div.conm > a.cona")
        search_results = [
            SearchResult(
                title = a.text,
                url = 'https://animefrenzy.net/' + a.get('href')
            )
            for a in titleName
        ]
        return(search_results)

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        lang = self.config.get("version")
        if lang == "subbed":
            ep_list = [x for x in soup.select("div.sub1 > a")]
        elif lang == "dubbed":
            ep_list = [x for x in soup.select("div.dub1 > a")]
        else:
            logger.warning("Wrong Language Setting, Defaulting to Subbed")
            ep_list = [x for x in soup.select("div.sub1 > a")]

        episodes = ["https://animefrenzy.net" + x.get("href") for x in ep_list]

        if len(episodes) == 0:
            logger.warning("No Episodes available, if lang is \"dubbed\" try switching to subbed")

        return episodes[::-1]
#        raise NotImplementedError

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.select_one("div.infodes > h1").text 

class AnimeFrenzyEpisode(AnimeEpisode, sitename='animefrenzy'):
    def _get_sources(self):
        logger.debug(self.url)
        soup = helpers.soupify(helpers.get(self.url))
        link = soup.select_one("div.host > a.btn-video")
        logger.debug(link)
        return [("vidstreaming", link.get("data-video-link"))]
#        raise NotImplementedError
