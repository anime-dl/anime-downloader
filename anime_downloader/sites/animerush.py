import logging
import re

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from anime_downloader.extractors import get_extractor
import sys

logger = logging.getLogger(__name__)

class AnimeRush(Anime, sitename='animerush'):
        """
        Nice things
        Siteconfig
        ----------
        server: primary server to use
        fallback_servers: servers to use if the primary server cannot be found (in order)
        """
        sitename = 'animerush'
        url = f'https://www.{sitename}.tv/search.php'
        @classmethod
        def search(cls, query):
            search_results = helpers.soupify(helpers.get(cls.url, params = {'searchquery':query}))
            title = search_results.select('h3') #Stored in another place
            results = search_results.select('a.highlightit')
            search_results = [
                SearchResult(
                    title=title[a].text,
                    url='https:'+ results[a].get('href'))
                for a in range(1,len(results))]
            return(search_results)

        def _scrape_episodes(self):
            soup = helpers.soupify(helpers.get(self.url)).select('div.episode_list > a')
            return ['https:' + a.get('href') for a in soup[::-1]]

        def _scrape_metadata(self):
            soup = helpers.soupify(helpers.get(self.url))
            self.title = soup.select('div.amin_week_box_up1 > h1')[0].text

class AnimeRushEpisode(AnimeEpisode, sitename='animerush'):
        def _get_sources(self):
            server = self.config['server']
            fallback = self.config['fallback_servers']

            soup = helpers.soupify(helpers.get(self.url))
            sources = ([[self._get_url('https:' + a.get('href')),a.text] for a in soup.select('div.episode_mirrors > div > h3 > a')])
            sources.append([self._get_url(self.url),soup.select('iframe')[-1].get('title')])
            
            for a in range (len(sources)): #Primary server
                if server == sources[a][1]:
                    if 'yourupload' in sources[a][0]:extractor = 'yourupload'
                    else:extractor = 'mp4upload'
                    return[(extractor,sources[a][0])]

            for a in range (len(sources)): #Fallback servers
                if sources[a][1] in fallback:
                    if 'yourupload' in sources[a][0]:extractor = 'yourupload'
                    else:extractor = 'mp4upload'
                    return[(extractor,sources[a][0])]
            
            if 'yourupload' in sources[0][0]:extractor = 'yourupload'
            else:extractor = 'mp4upload'
            return[(extractor,sources[0][0])]
        
        def _get_url(self,url): #The links are hidden on other pages
            soup = helpers.soupify(helpers.get(url))
            return (soup.select('iframe')[-1].get('src'))
