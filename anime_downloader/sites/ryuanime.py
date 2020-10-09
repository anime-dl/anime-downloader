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

    sitename = 'ryuanime'

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.get("https://ryuanime.com/browse-anime", params={"search": query}))
        result_data = soup.select("li.list-inline-item:has(p.anime-name):has(a.ani-link)")

        search_results = [
            SearchResult(
                title=result.select("p.anime-name")[0].text,
                url='https://ryuanime.com' + result.select("a.ani-link")[0].get("href")
            )
            for result in result_data
        ]
        return search_results

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        episodes = ['https://ryuanime.com' + x.get("href") for x in soup.select("li.jt-di > a")]

        if len(episodes) == 0:
            logger.warning("No episodes found")

        return episodes[::-1]

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.find("h1").text.strip()


class RyuAnimeEpisode(AnimeEpisode, sitename='ryuanime'):
    def getLink(self, name, _id):
        if name == "trollvid":
            return "https://trollvid.net/embed/" + _id
        elif name == "mp4upload":
            return f"https://mp4upload.com/embed-{_id}.html"
        elif name == "xstreamcdn":
            return f"https://xstreamcdn.com/v/" + _id

    def _get_sources(self):
        page = helpers.get(self.url).text

        # Example:
        """
        [
          {
            "host":"trollvid","id":"c4a94b4e50ee","type":"dubbed","date":"2019-08-01 20:48:01"}
            ...
          }
        ]
        """
        hosts = json.loads(re.search(r"let.*?episode.*?videos.*?(\[\{.*?\}\])", page).group(1))

        sources_list = []

        for host in hosts:
            name = host.get("host")
            _id = host.get("id")
            link = self.getLink(name, _id)

            if link:
                sources_list.append({
                    "extractor": name,
                    "url": link,
                    "server": name,
                    "version": host.get("type")
                })

        return self.sort_sources(sources_list)
