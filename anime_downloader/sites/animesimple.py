import logging
import re
import sys

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

class AnimeSimple(Anime, sitename='animesimple'):
        sitename = 'animesimple'
        url = f'https://{sitename}.com/search'
        @classmethod
        def search(cls, query):
            search_results = helpers.soupify(helpers.get(cls.url,
                                         params={'q': query})).select('div.card-body > div > a')
            title_data = {
                'data' : []
            }
            for a in range(len(search_results)):
                url = search_results[a].get('href')
                title = search_results[a].get('title')
                if title == None: #Different website design based on amout of search results
                    title = (search_results[a]).select('img')[0].get('alt')

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
            anime_id = soup.find(id = 'animeid').get('value')
            
            elements = helpers.soupify(helpers.get('https://animesimple.com/request',
                                        params={
                                        'anime-id': anime_id,
                                        'epi-page': '1',
                                        'top': 10000, #max 10 000 episodes
                                        'bottom': 0,
                                         }))
            return [a.get('href') for a in elements]

        def _scrape_metadata(self):
            soup = helpers.soupify(helpers.get(self.url)).select('h1.media-heading')
            regex = r'class="media-heading">[^<]*'
            self.title = re.search(regex,str(soup)).group().replace('class="media-heading">','')

class AnimeSimpleEpisode(AnimeEpisode, sitename='animesimple'):
        def _get_sources(self):
            soup = helpers.soupify(helpers.get(self.url))

            regex = r'var json = [^;]*'
            json = re.search(regex,str(soup)).group().replace('var json = ','') #Lots of sources can be found here
            
            trollvid = r"src='https:\\/\\/trollvid.net\\/embed\\/[^']*"
            embed = re.search(trollvid,json).group().replace('\\','').replace("src='",'')
            
            return [('trollvid', embed,)]
