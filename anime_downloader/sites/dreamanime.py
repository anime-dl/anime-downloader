
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import json
import re
import logging
import click

logger = logging.getLogger(__name__)

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
        soup = helpers.soupify(helpers.get("https://dreamanime.fun/search", params = {"term" : query}))
        result_data = soup.select("a#epilink")

        search_results = [
            SearchResult(
                title = result.text,
                url = result.get("href")
                )
            for result in result_data
            ]

        return search_results

    def _scrape_episodes(self, version = None):
        if version == None:
            version = self.config.get("version", "subbed")

        versions = [
                "subbed",
                "dubbed"
                ]

        soup = helpers.soupify(helpers.get(self.url))
 
        _all = soup.select("div.episode-wrap")
        episodes = [x.find("a").get("href") if "href" in [*x.find("a").attrs.keys()] else x.find("a").get("data-src") for x in _all if x.select(".ep-type")[0].text == version[0:3].title()]

        if len(episodes) == 0:
            newVersion = versions[int(not bool(versions.index(version)))]
            change = click.confirm(f"No {version} episodes found. Try {newVersion}")
            if change:
                return self._scrape_episodes(newVersion)

            logger.warning("No episodes found")


        return episodes[::-1]

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.find("div", {"class":"contingo"}).find("p").text

class DreamAnimeEpisode(AnimeEpisode, sitename='dreamanime'):
    def getLink(self, name, _id):
        if name == "trollvid":
            return "https://trollvid.net/embed/" + _id
        elif name == "mp4upload":
            return f"https://mp4upload.com/embed-{_id}.html"
        elif name == "xstreamcdn":
            return "https://www.xstreamcdn.com/v/" + _id

    def _get_sources(self):
        server = self.config.get("server", "trollvid")
        resp = helpers.get(self.url).text
        hosts = json.loads(re.search("var\s+episode\s+=\s+({.*})", resp).group(1))["videos"]
        _type = hosts[0]["type"]
        try:
            host = list(filter(lambda video: video["host"] == server and video["type"] == _type, hosts))[0]
        except IndexError:
            host = hosts[0]
            if host["host"] == "mp4upload" and len(hosts) > 1:
                host = hosts[1]

        name = host["host"]
        _id = host["id"]
        link = self.getLink(name, _id)

        return [(name, link)]
