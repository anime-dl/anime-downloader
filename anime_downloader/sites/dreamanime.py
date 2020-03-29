
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from urllib.parse import quote_plus
import json

class DreamAnime(Anime, sitename='dreamanime'):
    sitename='dreamanime'
    url = f'https://{sitename}.fun/search'

    @classmethod
    def search(cls, query):
        results = helpers.get("https://dreamanime.fun/search?term=" + quote_plus(query)).text
        soup = helpers.soupify(results)
        result_data = soup.find_all("a", {"id":"epilink"})

        search_results = [
            SearchResult(
                title = result.text,
                url = result.get("href")
                )
            for result in result_data
            ]

        return search_results

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        return [x.get("data-src") for x in soup.find_all("a", {"class":"ep-link-sub"})]

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.find("div", {"class":"contingo"}).find("p").text

class DreamAnimeEpisode(AnimeEpisode, sitename='dreamanime'):
    def _get_sources(self):
        soup = helpers.soupify(helpers.get(self.url))
        host = json.loads(soup.find("div", {"class":"spatry"}).previous_sibling.previous_sibling.text[21:-2])["videos"][0]
        name = host["host"]
        _id = host["id"]
        if name == "trollvid":
            link = "https://trollvid.net/embed/" + _id
        elif name == "vidstreaming":
            link = "https://vidstreaming.io/download?id=" + _id
        elif name == "mp4upload":
            link = f"https://mp4upload.com/embed-{_id}.html"

        return [(name, link)]

