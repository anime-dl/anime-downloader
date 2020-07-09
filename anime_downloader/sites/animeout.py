import logging
import re

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)

class AnimeOut(Anime, sitename='animeout'):
        sitename = 'animeout'
        url = f'https://{sitename}.xyz/'
        @classmethod
        def search(cls, query):
            search_results = helpers.soupify(helpers.get(cls.url, params={'s': query})).select('h3.post-title > a')
            return [
                SearchResult(
                    title = i.text,
                    url = i.get('href'))
                for i in search_results
            ]


        def _scrape_episodes(self):
            soup = helpers.soupify(helpers.get(self.url))
            elements = soup.select('article.post a')
            return [i.get('href') for i in elements if 'Direct Download' in i.text]


        def _scrape_metadata(self):
            soup = helpers.soupify(helpers.get(self.url))
            self.title = soup.select('h1.page-title')[0].text


class AnimeOutEpisode(AnimeEpisode, sitename='animeout'):
        def _get_sources(self):
            # Should probably be moved to a separate extractor.
            soup = helpers.soupify(helpers.get(self.url))
            link = soup.select('div.Center > p > h2 > a')[0].get('href')
            script = helpers.soupify(helpers.get(link)).select('script')[2]
            url = re.search(r'http[^"]*',str(script)).group()
            return [('no_extractor', url,)]
