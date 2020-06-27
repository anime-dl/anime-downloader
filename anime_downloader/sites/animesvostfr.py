import logging

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)

class AnimesVostFr(Anime, sitename='animesvostfr'):
    sitename = 'animesvostfr'

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.get("https://www2.animesvostfr.net", params = {"s": query}))
        
        search_results = [
                SearchResult(
                    title = x["oldtitle"],
                    url = x["href"]
                    )
                for x in soup.select("div.ml-item > a")
                ]
        
        return search_results

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        episodes = []
        visited = [self.url]

        while True:
            episodes.extend([x["href"] for x in soup.select("div.les-title > a")])
            nextPage = soup.select("a.page.larger")

            if len(nextPage) != 0 and nextPage[0]["href"] not in visited:
                soup = helpers.soupify(helpers.get(nextPage[0]["href"]))
                visited.append(nextPage[0]["href"])
            else:
                break

        return episodes

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.select("h1")[0].text

class AnimesVostFrEpisode(AnimeEpisode, sitename='animesvostfr'):
    def _get_sources(self):
       #TODO: support for other servers.
       server = "photoss"
       extractor_map = {"photoss": "comedyshow"}
       format_string = "https://animesvostfr.net/ajax-get-link-stream/?server={}&filmId={}"
       soup = helpers.soupify(helpers.get(self.url))
       episodeId = soup.select("option[selected=selected]")[0]["episodeid"]
       link = helpers.get(format_string.format(server, episodeId)).text

       if link:
           return [(extractor_map[server], link)]


       logger.warn("Could not find any supported servers")

