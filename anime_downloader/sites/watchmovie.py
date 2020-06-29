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
        servers: servers used in order
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
            soup = helpers.soupify(helpers.get(self.url))
            sources = soup.select('div.anime_muti_link > ul > li > a')

            #logger.debug('Sources: {}'.format([i.get('data-video') for i in sources]))

            extractors = { 
            #url             #Extractor   #Server in config
            'vidcloud9.com/':['vidstream','vidstream'],
            'hydrax.net/':['hydrax','hydrax'],
            'gcloud.live/v/':['gcloud','gcloud'],
            'yourupload.com/':['yourupload','yourupload'],
            }

            sources_list = []
            for i in sources:
                for j in extractors:
                    if j in i.get('data-video'):
                        sources_list.append({
                            'extractor':extractors[j][0],
                            'url':i.get('data-video'),
                            'server':extractors[j][1],
                            'version':'subbed'
                            })

            return self.sort_sources(sources_list)
