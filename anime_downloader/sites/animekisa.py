import logging
import re
import sys

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)

class AnimeKisa(Anime,sitename='animekisa'):    
    sitename = 'animekisa'
    url = f'https://animekisa.tv/'
    @classmethod
    def search(cls,query):
        search_results = helpers.soupify(helpers.get("https://animekisa.tv/search", params = {"q": query}))
        search_results = search_results.select('div.similarbox > a.an')
        search_results = [
            SearchResult(
                title = i.select('div > div > div > div > div.similardd')[0].text,
                url = 'https://www.animekisa.tv' + i.get('href'))
            for i in search_results if i.get('href') != '/'
            ]
        
        return search_results
    
    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title  = soup.select('h1.infodes')[0].text
    
    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        episode_links = soup.select('a.infovan')
        episodes = [
            'https://animekisa.tv'+'/'+i.get('href')
        for i in episode_links[::-1]]
        return episodes

class AnimeKisaEpisode(AnimeEpisode,sitename = 'animekisa'):
    def _get_sources(self):
        soup = helpers.get(self.url).text
        server = self.config['server']
        fallback = self.config['fallback_servers']
        regex = {
        'mp4upload': r'(https://www.mp4upload.com/)+[^"]*',
        'vidstream': r'(https://vidstreaming.io/)+[^"]*',
        'gcloud':    r'(https://gcloud.live/)+[^"]*',
        }
        if re.search(regex[server],soup): #Testing sources with selected provider
            link = re.search(regex[server],soup).group()
            return [(server, link,)]

        logger.debug('Preferred server %s not found. Trying all supported servers',server)

        for a in fallback: #Testing fallback providers
            if re.search(regex[a],soup):
                link = re.search(regex[a],soup).group()
                return [(a, link,)]

        logger.debug('No supported servers found')
        return ''
