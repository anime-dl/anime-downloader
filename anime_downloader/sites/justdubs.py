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
        server_links = {
            'mp4upload':'https://mp4upload.com/embed-{}.html',
            'gcloud':'https://gcloud.live/v/{}',
            'fembed':'https://www.fembed.com/v/{}',
        }
        soup = helpers.soupify(helpers.get(self.url))
        link = soup.find_all('iframe')
        regexmp4 = 'https://mp4upload.com/'
        regexgc = 'https://gcloud.live/'
        regexfe = 'https://www.fembed.com/'
        returnServer = ""
        returnLink = ""
        for x in link:
            y = x.get("src")
            logger.debug(y)
            if re.search(regexmp4, y) != "None":
                returnServer = 'mp4upload'
                returnLink = y
                logger.debug("MP4Upload")
                return [('mp4upload', y)]
            elif re.search(regexgc, y) != "None":
                returnServer = 'gcloud'
                returnLink = y
                logger.debug("gcloud")
                return [('gcloud', y)]
            elif re.search(regexfe, y) != "None":
                returnServer = 'fembed'
                returnLink = y
                logger.debug("Fembed")
                return [('fembed', y)]
#
#
#        logger.debug(link)
#        return [(returnServer, y)]
#        hosts = json.loads(soup.select(f"div.tab-pane iframe[src*='{server_links['mp4upload' or 'gcloud' or 'fembed']}']".format(server_links)))
#        logger.debug(hosts)
#        _type = hosts[0]["type"]
#
#        for i in link:
#            link[i].get("src")
#            if server_links["mp4upload"] in link[i]:
#                return [('mp4upload', link[i])]
#            elif server_links["gcloud"] in link[i]:
#                return [('gcloud', link[i])]
#            elif server_links['fembed'] in link[i]:
#                return [('fembed'), link[1]]
#
#        try:
#            host = list(filter(lambda video: video["host"] == server and video["type" == _type, hosts]))[0]
#        except IndexError:
#            host = hosts[0]
#            if host["host"] == "mp4upload" and len(hosts) > 1:
#                host = hosts[1]
#        name = host["host"]
#        _id = host["id"]
#        link = self.getLink(name, _id)
#        return [('mp4upload', link)]