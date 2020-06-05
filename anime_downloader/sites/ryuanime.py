
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import json
import re
import logging

logger = logging.getLogger(__name__)

class RyuAnime(Anime, sitename='ryuanime'):
    """
    Site: http://www4.ryuanime.com
    Config
    ------
    version: One of ['subbed', 'dubbed']
        Selects the version of audio of anime.
    server: One of ['mp4upload', 'trollvid']
        Selects the server to download from.
    """

    sitename='ryuanime'

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.get("https://www4.ryuanime.com/search", params = {"term" : query}))
        result_data = soup.select("ul.list-inline")[0].select("a")

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
        ep_list = [x for x in soup.select("div.col-sm-6") if x.find("h5").text == version.title()][0].find_all("a")
        episodes = [x.get("href") for x in ep_list]

        if len(episodes) == 0:
            logger.warning("No episodes found")

        return episodes[::-1]

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.select("div.card-header")[0].find("h1").text

class RyuAnimeEpisode(AnimeEpisode, sitename='ryuanime'):
    def getLink(self, name, _id):
        if name == "trollvid":
            return "https://trollvid.net/embed/" + _id
        elif name == "mp4upload":
            return f"https://mp4upload.com/embed-{_id}.html"
        elif name == "xstreamcdn":
            return f"https://xstreamcdn.com/v/" + _id

    def _get_sources(self):
        server = self.config.get("server", "trollvid")
        soup = helpers.soupify(helpers.get(self.url))
        
        hosts = json.loads(re.search("\[.*?\]", soup.select("div.col-sm-9")[0].select("script")[0].text).group())

        _type = hosts[0]["type"]
        try:
            host = list(filter(lambda video: video["host"] == server and video["type"] == _type, hosts))[0]
        except IndexError:
            host = hosts[0]
            #I will try to avoid mp4upload since it mostly doesn't work
            if host["host"] == "mp4upload" and len(hosts) > 1:
                host = hosts[1]

        name = host["host"]
        _id = host["id"]
        link = self.getLink(name, _id)

        return [(name, link)]
