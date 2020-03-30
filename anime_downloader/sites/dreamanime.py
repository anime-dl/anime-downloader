
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import json
import re

class DreamAnime(Anime, sitename='dreamanime'):
    """
    Site: http://dreamanime.fun
    Config
    ------
    version: One of ['subbed', 'dubbed']
        Selects the version of audio of anime.
    server: One of ['mp4upload', 'trollvid']
        Selects the server to download from.
    """

    sitename='dreamanime'

    @classmethod
    def search(cls, query):
        results = helpers.get("https://dreamanime.fun/search", params = {"term" : query}).text
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
        version = self.config.get("version", "subbed")
        soup = helpers.soupify(helpers.get(self.url))
        subbed = []
        dubbed = []
        _all = soup.find_all("div", {"class":"episode-wrap"})
        for i in _all:
            ep_type = i.find("div", {"class":re.compile("ep-type type-.* dscd")}).text
            if ep_type == 'Sub':
                subbed.append(i.find("a").get("data-src"))
            elif ep_type == 'Dub':
                dubbed.append(i.find("a").get("href"))
        return eval(version)

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.find("div", {"class":"contingo"}).find("p").text

class DreamAnimeEpisode(AnimeEpisode, sitename='dreamanime'):
    def _get_sources(self):
        server = self.config.get("server", "trollvid")
        soup = helpers.soupify(helpers.get(self.url))
        hosts = json.loads(soup.find("div", {"class":"spatry"}).previous_sibling.previous_sibling.text[21:-2])["videos"]
        type = hosts[0]["type"]
        host = list(filter(lambda video: video["host"] == server and video["type"] == type, hosts))[0]
        name = host["host"]
        _id = host["id"]
        if name == "trollvid":
            link = "https://trollvid.net/embed/" + _id
        elif name == "mp4upload":
            link = f"https://mp4upload.com/embed-{_id}.html"
        return [(name, link)]
