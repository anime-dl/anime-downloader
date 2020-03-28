import logging
import re

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

class Dubbedanime(Anime, sitename='dubbedanime'):
        sitename = 'dubbedanime'
        url = f'https://{sitename}.net'
        @classmethod
        def search(cls, query):
            search_results = helpers.post(f'https://ww5.dubbedanime.net/ajax/paginate',
            data={
                'query[search]': query,
                'what': 'query',
                'model': 'Anime',
                'size': 30,
                'letter': 'all',
            }).json()
            search_results = [
                SearchResult(
                    title=search_results['results'][a]['title'],
                    url=cls.url + search_results['results'][a]['url'])
                for a in range(len(search_results['results']))
            ]
            return(search_results)

        def _scrape_episodes(self):
            soup = helpers.soupify(helpers.get(self.url))
            elements = soup.find("ul", {"id": "episodes-grid"}).select('li > div > a')
            return [('https://dubbedanime.net' + a.get('href')) for a in elements[::-1]]

        def _scrape_metadata(self):
            soup = helpers.soupify(helpers.get(self.url))
            self.title= soup.select('h1.h3')[0].text

class DubbedanimeEpisode(AnimeEpisode, sitename='dubbedanime'):
        def _get_sources(self):
            soup = helpers.soupify(helpers.get(self.url)).text

            x = re.search(r"xuath = '([^']*)", soup).group(1)
            token = re.search(r'"trollvid","id":"([^"]*)', soup).group(1)

            url = f'https://mp4.sh/embed/{token}{x}'
            return [('mp4sh', url)]

