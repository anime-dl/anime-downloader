import re
from anime_downloader.extractors import get_extractor
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import logging

logger = logging.getLogger(__name__)

class AnimeVibe(Anime, sitename='animevibe'):
        sitename = 'animevibe'
        url = f'https://{sitename}.tv'
        @classmethod
        def search(cls, query):
            search_results = helpers.soupify(helpers.get(cls.url,params={'s':query})).select('h5.title-av-search-res > a')
            return [
                SearchResult(
                    title = a.text,
                    url = a.get('href'))
                for a in search_results
            ]


        def _scrape_episodes(self):
            #First episode
            episodes = [self.url]
            soup = helpers.soupify(helpers.get(self.url))
            episodes.extend([x.get('href') for x in soup.select('div.wrap-episode-list > a')])
            return episodes


        def _scrape_metadata(self):
            soup = helpers.soupify(helpers.get(self.url))
            self.title = soup.select('h3.av-episode-title')[0].text


class AnimeVibeEpisode(AnimeEpisode, sitename='animevibe'):
        def _get_sources(self):
            soup = helpers.soupify(helpers.get(self.url))
            iframe = soup.select('iframe')[0]
            logger.debug('iframe: {}'.format('iframe'))
            embed = 'https://animevibe.tv' + str(iframe.get('src'))
            sources = helpers.soupify(helpers.get(embed)).select('option')
            logger.debug('Sources: {}'.format(sources))
            sources_list = []
            extractors = [ 
                '3rdparty',
                'mp4upload',
                'fembed',
                'gcloud',
                'vidstream',
                'hydrax'
            ]

            prefix = 'https://animevibe.tv/players/'
            for i in sources:
                source = None
                url = i.get('value').replace('iframe.php?vid=','')
                url = prefix + url if url.startswith('3rdparty') else url
                #Choosing 3rd-party link is not implemented yet
                for j in extractors:
                    #the 3rd-party url can contain other extractors
                    if j in url and not ('3rdparty' in url and j != '3rdparty'):
                        extractor = 'gcloud' if j == 'fembed' else j #fembed gets passed to gcloud too
                        source = {
                        'extractor':extractor,
                        'server':j,
                        'url':url,
                        'version':'subbed'
                        }

                if source:
                    sources_list.append(source)

            logger.debug('sources_list: {}'.format(sources_list))
            return self.sort_sources(sources_list)
