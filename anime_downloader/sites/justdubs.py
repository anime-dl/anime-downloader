import logging
import json
import re

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
    def _get_sources(self):
        server = self.config['server']
        #server_links = {
        #    'mp4upload':'https://mp4upload.com/embed-{}.html',
        #    'gcloud':'https://gcloud.live/v/{}',
        #    'fembed':'https://www.fembed.com/v/{}',
        #}
        soup = helpers.soupify(helpers.get(self.url))
        link = soup.find('iframe').get("src")
        #hosts = json.loads(soup.select(f"div.tab-pane iframe[src*='{server_links['mp4upload' or 'gcloud' or 'fembed']}']".format(server_links)))
        #logger.debug(hosts)
        #_type = hosts[0]["type"]
        

        #try:
        #    host = list(filter(lambda video: video["host"] == server and video["type" == _type, hosts]))[0]
        #except IndexError:
        #    host = hosts[0]
        #    if host["host"] == "mp4upload" and len(hosts) > 1:
        #        host = hosts[1]
        #name = host["host"]
        #_id = host["id"]
        #link = self.getLink(name, _id)
        return [('mp4upload', link)]