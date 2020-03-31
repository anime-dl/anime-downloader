
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import json

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
        results = helpers.get("https://www4.ryuanime.com/search", params = {"term" : query}).text
        soup = helpers.soupify(results)
        result_data = soup.find("ul", {"class" : "list-inline"}).find_all("a")

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
        ep_list = [x for x in soup.find_all("div", {"class":"col-sm-6"}) if x.find("h5").text == version.title()][0].find_all("a")
        episodes = [x.get("href") for x in ep_list]
        return episodes

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.find("div", {"class" : "card-header"}).find("h1").text

class RyuAnimeEpisode(AnimeEpisode, sitename='ryuanime'):
    def _get_sources(self):
        server = self.config.get("server", "trollvid")
        soup = helpers.soupify(helpers.get(self.url))
        hosts = json.loads(soup.find("div", {"class":"col-sm-9"}).find("script").text[30:-6])
        _type = hosts[0]["type"]
        host = list(filter(lambda video: video["host"] == server and video["type"] == _type, hosts))[0]
        name = host["host"]
        _id = host["id"]
        if name == "trollvid":
            link = "https://trollvid.net/embed/" + _id
        elif name == "mp4upload":
            link = f"https://mp4upload.com/embed-{_id}.html"
        return [(name, link)]
