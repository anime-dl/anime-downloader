import logging
import re

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

class AnimeOut(Anime, sitename='animeout'):
        sitename = 'animeout'
        url = f'https://{sitename}.xyz/'
        @classmethod
        def search(cls, query):
            search_results = helpers.soupify(helpers.get(cls.url,
                                         params={'s': query})).select('h3.post-title > a')

            title_data = {
                'data' : []
            }
            for a in range(len(search_results)):
                url = search_results[a].get('href')
                title = search_results[a].text
                data = {
                    'url' : url,
                    'title' : title,
                }
                title_data['data'].append(data)

            search_results = [
                SearchResult(
                    title=result["title"],
                    url=result["url"])
                for result in title_data.get('data', [])
            ]
            return(search_results)

        def _scrape_episodes(self):
            soup = helpers.soupify(helpers.get(self.url))
            elements = soup.select('div.article-content > p > a')

            episode_links = []
            for a in elements:
                if 'Direct Download' in a.text:
                    episode_links.append(a.get('href'))
            return [a for a in episode_links]

        def _scrape_metadata(self):
            soup = helpers.soupify(helpers.get(self.url))
            self.title = soup.select('h1.page-title')[0].text

class AnimeOutEpisode(AnimeEpisode, sitename='animeout'):
        def _get_sources(self):
            soup = helpers.soupify(helpers.get(self.url))
            link = soup.select('div.Center > p > h2 > a')[0].get('href')
            script = helpers.soupify(helpers.get(link)).select('script')[2].text
            url = re.search(r'http[^"]*',script).group()
            return [('no_extractor', url,)]
