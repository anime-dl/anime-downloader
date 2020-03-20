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

            title_data = {
                'data' : []
            }
            for a in range(len(search_results['results'])):
                url = cls.url + search_results['results'][a]['url']
                title = search_results['results'][a]['title']
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
            elements = soup.find("ul", {"id": "episodes-grid"}).select('li > div > a')

            episode_links = []
            for a in elements[::-1]:
                episode_links.append('https://dubbedanime.net' + a.get('href'))

            return [a for a in episode_links]

        def _scrape_metadata(self):
            soup = helpers.soupify(helpers.get(self.url))
            self.title= soup.select('h1.h3')[0].text

class DubbedanimeEpisode(AnimeEpisode, sitename='dubbedanime'):
        def _get_sources(self):
            # TODO: refractor to extractor
            soup = helpers.soupify(helpers.get(self.url)).text
            xuath = r"xuath = '[^']*"
            x = re.search(xuath,soup).group().split("xuath = '")[1]
            tokenregex = r'"trollvid","id":"[^"]*'
            token = re.search(tokenregex,soup).group(0).split('"trollvid","id":"')[1]
            url = f'https://mp4.sh/embed/{token}{x}'

            soup = helpers.get(url, referer=self.url).text
            url = re.search(r'source src="[^"]*',soup).group().split('source src="')[1]

            return [('no_extractor', url,)]
