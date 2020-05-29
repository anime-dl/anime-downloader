import logging
import json

from anime_downloader.sites.exceptions import AnimeDLError, NotFoundError
from anime_downloader import util
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)

class JustDubs(Anime, sitename='justdubs'):
    sitename = 'justdubs'
    @classmethod
    def search(cls, query):
        results = helpers.get(f"http://justdubs.org/search/node/{query}").text
        soup = helpers.soupify(results)
        results_data = soup.select("li.search-result a[href*='http://justdubs.org/watch-']")
        logger.debug(results_data)
        search_results = [
            SearchResult(
                title = result.text,
                url = result.get("href")
            )
            for result in results_data
        ]
        return search_results

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        ret = [str(a['href'])
                for a in soup.find_all('a', {'class' : 'list-group-item'})]
        if ret == []:
            err = 'No Episodes Found in url "{}"'.format(self.url)
            args = [self.url]
            raise NotFoundError(err, *args)
        return list(reversed(ret))

class JustDubsEpisode(AnimeEpisode, sitename='justdubs'):
    def getLink(self, name, _id):
        if name == "Source: 1":
            return f"https://mp4upload.com/embed-{_id}.html"
        elif name == "Source: 2":
            return f"https://xstreamcdn.com/v/" + _id

    def _get_sources(self):
        raise NotImplementedError
        server = self.config['server']
        soup = helpers.soupify(helpers.get(self.url))
        hosts = json.loads(soup.find(""))
        