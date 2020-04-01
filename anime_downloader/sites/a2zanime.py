import logging
import re

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

class A2zanime(Anime, sitename='a2zanime'):
        sitename = 'a2zanime'
        url = f'https://{sitename}.com'

        @classmethod
        def search(cls, query):
            search_results = helpers.soupify(helpers.get(f'{cls.url}/search?url=search&q={query}')).select('div.main-con > a')
            search_results = [
                SearchResult(
                    title=search_results[a].get('title'),
                    url=cls.url + search_results[a].get('href'))
                for a in range(len(search_results))
            ]
            return(search_results)

        def _scrape_episodes(self):
            soup = helpers.soupify(helpers.get(self.url))
            elements = soup.select('div.card-bodyu > a')
            return [('https://a2zanime.com' + a.get('href')) for a in elements[::-1]]

        def _scrape_metadata(self):
            soup = helpers.soupify(helpers.get(self.url))
            self.title = soup.select('h1.title')[0].text

class A2zanimeEpisode(AnimeEpisode, sitename='a2zanime'):
        def _get_sources(self):
            #You can get multiple sources from this
            soup = helpers.soupify(helpers.get(self.url))
            regex = r"data-video-link=\"(//[^\"]*)"
            url = 'https:' + re.search(regex,str(soup)).group(1)
            
            soup = helpers.soupify(helpers.get(url))
            url = (soup.select('div > iframe')[0].get('src'))
            
            return [('vidstream', url ,)]

