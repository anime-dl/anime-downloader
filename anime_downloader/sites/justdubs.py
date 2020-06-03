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

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.select('h1.page-header')[0].text

class JustDubsEpisode(AnimeEpisode, sitename='justdubs'):
    def _get_sources(self):
        servers = self.config['servers']
        
        """maps urls to extractors"""
        server_links =  { 
        'mp4upload':'mp4upload.com',
        'gcloud':'gcloud.live',
        'gcloud':'fembed.com'
        }

        soup = helpers.soupify(helpers.get(self.url)).select('iframe')
        
        for a in servers:
            for b in soup:
                for c in server_links:
                    if server_links[c] in b.get('src') and a == c:
                        return [(c, b.get('src'))]
        
        logger.warn("Unsupported URL")
        return ""
