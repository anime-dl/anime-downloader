import logging
import re
import sys
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)

class WatchMovie(Anime, sitename='watchmovie'):
        """
        Nice things
        Siteconfig
        ----------
        server: Primary server to use (Default: gcloud)
        fallback_servers: Recorded working servers which is used if the primary server cannot be found
        """
        sitename = 'watchmovie'
        url = f'https://{sitename}.movie'
        @classmethod
        def search(cls, query):
            search_results = helpers.soupify(helpers.get(cls.url+'/search.html',params={'keyword': query})).select('a.videoHname')
            
            search_results = [
                SearchResult(
                    title=a.get('title'),
                    url=cls.url+a.get('href'))
                for a in search_results
            ]
            return(search_results)

        def _scrape_episodes(self):
            if 'anime-info' in self.url:
                url = self.url.replace('anime-info','anime') + '/all'
            else:
                url = self.url+'/season'
            soup = helpers.soupify(helpers.get(url)).select('a.videoHname')
            return ['https://watchmovie.movie'+a.get('href') for a in soup[::-1]]

        def _scrape_metadata(self):
            self.title = helpers.soupify(helpers.get(self.url)).select('div.page-title > h1')[0].text
            
class WatchMovieEpisode(AnimeEpisode, sitename='watchmovie'):
        def _get_sources(self):
            server = self.config['server']
            fallback = self.config['fallback_servers']

            soup = helpers.soupify(helpers.get(self.url))
            sources = soup.select('div.anime_muti_link > ul > li > a')

            for a in sources: 
                url = a.get('data-video')
                if server in url:
                    if server == 'fembed':extractor = 'gcloud'
                    else:extractor = server
                    return [(extractor, url,)]
            
            logger.debug('Preferred server "%s" not found. Trying all supported servers.',self.config['server'])
            for a in sources: 
                url = a.get('data-video')
                for b in fallback:
                    if b in url:
                        if b == 'fembed':extractor = 'gcloud'
                        else:extractor = server
                        return [(extractor, url,)]
            
            logger.warning('No supported servers found. Trying all servers. This will most likely not work')
            return [('no_extractor', sources[0].get('data-video'),)]
