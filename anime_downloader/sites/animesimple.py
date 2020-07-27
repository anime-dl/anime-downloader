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
        return [
            SearchResult(
                title=i.get('title') if i.get('title') else i.select('img')[0].get('alt'),
                url=i.get('href'))
            for i in search_results
        ]


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
        return [i.get('href') for i in elements]


    def _scrape_metadata(self):
        self.title = helpers.soupify(helpers.get(self.url)).select('li.breadcrumb-item.active')[0].text


class AnimeSimpleEpisode(AnimeEpisode, sitename='animesimple'):
    def _get_sources(self):
        soup = helpers.soupify(helpers.get(self.url))
        regex = r'var json = ([^;]*)'
        sources = json.loads(re.search(regex,str(soup)).group(1)) #Lots of sources can be found here

        logger.debug('Sources: {}'.format(sources))

        sources_list = []
        for i in sources:        
            extractor = 'no_extractor' if not get_extractor(i['host']) else i['host']
            embed = re.search(r"src=['|\"]([^\'|^\"]*)",str(i['player']), re.IGNORECASE).group(1)
            sources_list.append({
            'extractor':extractor,
            'url':embed,
            'server':i['host'],
            'version':i.get('type','subbed')
            })

        return self.sort_sources(sources_list)
