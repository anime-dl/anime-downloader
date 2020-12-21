from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import re
import logging

logger = logging.getLogger(__name__)


class FastAni(Anime, sitename="fastani"):

    sitename = 'fastani'

    @classmethod
    def getToken(cls):
        resp = helpers.get("https://fastani.net")
        site_text = resp.text
        cookies = resp.cookies

        # Path to js file, e.g /static/js/main.f450dd1c.chunk.js - which contains the token
        js_location = "https://fastani.net" + re.search(r"src=\"(\/static\/js\/main.*?)\"", site_text).group(1)
        js = helpers.get(js_location).text

        # Get authorization token, e.g: {authorization:"Bearer h8X2exbErErNSxRnr6sSXAE2ycUSyrbU"}
        key, token = re.search("method:\"GET\".*?\"(.*?)\".*?\"(.*?)\"", js).group(1,2)

        return ({key: token}, cookies)

    @classmethod
    def search(cls, query):
        headers, cookies = cls.getToken()
        results = helpers.get(f"https://fastani.net/api/data?page=1&search={query}&tags=&years=", headers=headers, cookies=cookies).json()

        return [
            SearchResult(
                title=x.get('title').get("english"),
                # Need to know selected anime and original query for _scrape_episodes
                url=f"https://fastani.net/{selected}/{query}"
            )
            for selected, x in zip(range(len(results["animeData"]["cards"])), results["animeData"]["cards"])
        ]

    def _scrape_episodes(self):
        headers, cookies = self.getToken()
        split = self.url.split("/")
        query, selected = split[-1], int(split[-2])
        anime = helpers.get(f"https://fastani.net/api/data?page=1&search={query}&tags=&years=", headers=headers, cookies=cookies).json()

        cdnData = anime["animeData"]["cards"][selected]["cdnData"]

        # Get all episodes from all seasons of the anime
        # JSON Example:
        """
        {
        'seasons': [{
          'episodes': [{
            'file': 'https://private.fastani.net/Naruto/Season 1/Naruto S01E001.mp4',
        'directory': 'https://private.fastani.net/Naruto/Season 1',
        'timestamp': '2020-09-11T16:22:48.744Z',
        'thumb': 'https://private.fastani.net/Naruto/Season 1/thumbs/20_thumbnail_001.jpg',
        'title': 'Enter: Naruto Uzumaki!'
        }
            ...
          ]
        }
        """
        episodes = [j["file"] for i in [x["episodes"] for x in cdnData["seasons"]] for j in i]

        return episodes

    def _scrape_metadata(self):
        headers, cookies = self.getToken()
        split = self.url.split("/")
        query, selected = split[-1], int(split[-2])
        anime = helpers.get(f"https://fastani.net/api/data?page=1&search={query}&tags=&years=", headers=headers, cookies=cookies).json()
        self.title = anime["animeData"]["cards"][selected]["title"]["english"]


class FastAniEpisode(AnimeEpisode, sitename='fastani'):
    def _get_sources(self):
        return [("no_extractor", self.url)]
