import logging
import re
import json

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from anime_downloader.extractors import get_extractor

logger = logging.getLogger(__name__)

class AnimeSimple(Anime, sitename='animesimple'):
        sitename = 'animesimple'
        url = f'https://{sitename}.com/search'
        @classmethod
        def search(cls, query):
            search_results = helpers.soupify(helpers.get(cls.url, params={'q': query})).select('div.card-body > div > a')
            search_results = [
                SearchResult(
                    title=a.get('title') if a.get('title') != None else a.select('img')[0].get('alt'),
                    url=a.get('href'))
                for a in search_results
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
            regex = r'class="media-heading">([^<]*)'
            self.title = re.search(regex,str(soup)).group(1).strip()

class AnimeSimpleEpisode(AnimeEpisode, sitename='animesimple'):
        def _get_sources(self):
            server = self.config['server']

            soup = helpers.soupify(helpers.get(self.url))

            regex = r'var json = ([^;]*)'
            sources = json.loads(re.search(regex,str(soup)).group(1)) #Lots of sources can be found here


            for a in sources: #Testing sources with selected language and provider
                if a['type'] == self.config['version']:
                    if a['host'] == self.config['server']:
                        if get_extractor(a['host']) == None:server = 'no_extractor'
                        else:server = (a['host'])

                        embed = re.search(r"src=['|\"]([^\'|^\"]*)",str(a['player']),re.IGNORECASE).group(1)
                        return [(server, embed,)]

            logger.debug('Preferred server %s not found. Trying all supported servers in selected language.',server)

            for a in sources: #Testing sources with selected language
                if a['type'] == self.config['version']:
                    if get_extractor(a['host']) == None:server = 'no_extractor'
                    else:server = (a['host'])

                    embed = re.search(r"src=['|\"]([^\'|^\"]*)",str(a['player']),re.IGNORECASE).group(1)
                    return [(server, embed,)]

            logger.debug('No %s servers found, trying all servers',self.config['version'])

            if get_extractor(sources[0]['host']) == None:server = 'no_extractor'
            else:server = (sources[0]['host'])

            embed = re.search(r"src=['|\"]([^\'|^\"]*)",str(sources[0]['player']),re.IGNORECASE).group(1)
            return [(server, embed,)]
