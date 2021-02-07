
from anime_downloader.sites import helpers
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult

import logging

logger = logging.getLogger(__name__)


class AnimeHeros(Anime, sitename='animeheros'):
    sitename = 'animeheros'

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.get(
            f"https://{cls.sitename}.com/browse", params={"search": query}))
        results = soup.select("div.col-md-3.col-6 > a[href]")

        return [
            SearchResult(
                title=x.find("p").text.strip(),
                url=x.get("href")
            )
            for x in results
        ]

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        nextPageSelector = "[rel=next]"
        episodeSelector = ".list-group-item-action"

        results = [(int(x.find("div").text.split(":")[0].strip()),
                    x.get("href")) for x in soup.select(episodeSelector)]

        while soup.select(nextPageSelector):
            soup = helpers.soupify(helpers.get(
                soup.select(nextPageSelector)[0].get("href")))
            results.extend([(int(x.find("div").text.split(":")[0].strip()), x.get(
                "href")) for x in soup.select(episodeSelector)])

        logger.info(results)
        return results


class AnimeHerosEpisode(AnimeEpisode, sitename='animeheros'):
    def _get_sources(self):
        return [("no_extractor", self.url)]
