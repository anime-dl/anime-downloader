
import logging
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)


class SubsPlease(Anime, sitename="subsplease"):
    sitename = "subsplease"
    api_url = "https://subsplease.org/api"

    @classmethod
    def search(cls, query):

        # Tz for time zone - the parameter is required, but the value does not matter
        resp = helpers.get(cls.api_url, params={
                           "f": "search", "tz": "", "s": query}).json()

        if type(resp) is list:
            return

        # Using to deduplicate
        slug_to_title_dict = dict(
            [(resp[key]["show"], resp[key]["page"]) for key in resp.keys()])

        search_results = [
            SearchResult(
                title=x[0],
                url="https://subsplease.org/shows/" + x[1],
            )
            for x in slug_to_title_dict.items()
        ]

        return search_results

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))

        # Show ID
        sid = soup.select("[sid]")[0]["sid"]
        resp = helpers.get(self.api_url, params={
                           "f": "show", "tz": "", "sid": sid}).json()

        episodes = []

        for episode in resp["episode"].keys():
            # Construct a fake url for AnimeEpisode to use
            episodes.append(f"{self.url}/episode/{sid}/{episode}")

        return episodes[::-1]


class SubsPleaseEpisode(AnimeEpisode, sitename="subsplease"):
    QUALITIES = ["1080p", "720p", "480p"]

    def _get_sources(self):
        episode_name = self.url.split("/")[-1]
        sid = self.url.split("/")[-2]

        resp = helpers.get(SubsPlease.api_url, params={
                           "f": "show", "tz": "", "sid": sid}).json()

        downloads = resp["episode"][episode_name]["downloads"]

        # dict of quality-magnet
        magnets = dict([(x["res"] + 'p', x["magnet"]) for x in downloads])

        return [("no_extractor", magnets[self.quality])]
