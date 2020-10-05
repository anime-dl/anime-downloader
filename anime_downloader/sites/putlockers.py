
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from urllib.parse import quote_plus


class PutLockers(Anime, sitename="putlockers"):
    sitename="putlockers"

    @classmethod
    def search(cls, query):
        search_url="http://putlockers.fm/search-movies/{}.html".format(quote_plus(query))
        soup=helpers.soupify(helpers.get(search_url))

        search_results=[
                SearchResult(
                    title=x.find("img").get("alt"),
                    url=x.get("href")
                )
                for x in soup.select("div.item > a")
        ]

        return search_results

    def _scrape_episodes(self):
        soup=helpers.soupify(helpers.get(self.url))
        eps=soup.select("a.episode.episode_series_link")

        if not eps:
            eps.append(self.url)

        return eps

    def _scrape_metadata(self):
        soup=helpers.soupify(helpers.get(self.url))
        self.title=soup.find("h1").text

class PutLockersEpisode(AnimeEpisode, sitename="putlockers"):
    def _get_sources(self):
        return [("eplay", self.url)]
