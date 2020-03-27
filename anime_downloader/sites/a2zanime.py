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

            title_data = {
                'data' : []
            }
            for a in range(len(search_results)):
                url = cls.url + search_results[a].get('href')
                title = search_results[a].get('title')
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
            #print(soup)
            elements = soup.select('div.card-bodyu > a')


            episode_links = []
            for a in elements[::-1]:
                episode_links.append('https://a2zanime.com' + a.get('href'))

            return [a for a in episode_links]

        def _scrape_metadata(self):
            soup = helpers.soupify(helpers.get(self.url))
            self.title = soup.select('h1.title')[0].text

class A2zanimeEpisode(AnimeEpisode, sitename='a2zanime'):
        def _get_sources(self):
            #You can get multiple sources from this
            soup = helpers.soupify(helpers.get(self.url))
            regex = r"data-video-link=\"//[^\"]*"
            url = 'https:' + re.search(regex,str(soup)).group().replace('data-video-link="','')

            soup = helpers.soupify(helpers.get(url))
            url = (soup.select('div > iframe')[0].get('src'))

            soup = helpers.soupify(helpers.get(url))
            url = re.search(r'https://vidstreaming\.io/download\?[^"]*',str(soup)).group()

            soup = helpers.soupify(helpers.get(url))
            url = soup.select('div.dowload > a')[0].get('href')

            return [('no_extractor', url ,)]
