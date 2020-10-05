
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from urllib.parse import quote_plus

import base64
import re


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
        self.headers={"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/56.0"}
        text=helpers.get(self.url).text
        link=helpers.soupify(base64.b64decode(re.search('Base64.decode\("(.*)"\)', text).group(1)).decode()).iframe.get("src")
        return [("eplay", link)]
