import logging
import re
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)

class Yify(Anime, sitename='yify'):
        sitename = 'yify'
        url = f'https://{sitename}.mx/search'
        @classmethod
        def search(cls, query):
            search_results = helpers.soupify(helpers.get(cls.url, params={'keyword': query})).select('div.ml-item > a')
            return [
                SearchResult(
                    title=i.get('title'),
                    url=i.get('href')+'/watching.html')
                for i in search_results
            ]


        def _scrape_episodes(self):
            soup = helpers.soupify(helpers.get(self.url))
            regex = r'id:.*?\"([0-9]*?)\"'
            movie_id = re.search(regex,str(soup)).group(1)
            load_episodes = f'https://yify.mx/ajax/v2_get_episodes/{movie_id}'
            elements = helpers.soupify(helpers.get(load_episodes)).select('div.les-content > a')
            # Doesn't really return urls, rather ID:s. This is to prevent loading all episodes with separate
            # requests if the user only wants one episode
            return [i.get('episode-id','') for i in elements]


        def _scrape_metadata(self):
            soup = helpers.soupify(helpers.get(self.url))
            self.title = soup.select('title')[0].text.replace('Full Movie Free Yify','')


class YifyEpisode(AnimeEpisode, sitename='yify'):
        def _get_sources(self):
            if not self.url:
                return ''

            load_embed = 'https://yify.mx/ajax/load_embed/{}'
            embed = helpers.get(load_embed.format(self.url)).json()
            logger.debug('Embed: {}'.format(embed))
            embed_url = embed['embed_url']

            episode_id = embed_url.split('#')[-1]
            load_embed = f'https://yify.mx/ajax/load_embed_url/{episode_id}'
            episode_info = helpers.get(load_embed).json()
            logger.debug(episode_info)

            url = episode_info['url']
            api_id = re.search(r'id=([^&]*)',url).group(1)
            api = f'https://watch.yify.mx/api/?id={api_id}'
            sources = helpers.get(api).json()
            logger.debug(sources)

            sources_list = []
            extractors = {
            'yify.mx/embed/':['yify','yify'],
            'vidcloud9.com/':['vidstream','vidstream']
            }

            for i in sources:
                for j in extractors:
                    if j in i['link']:
                        sources_list.append({
                            'extractor':extractors[j][0],
                            'url':i['link'],
                            'server':extractors[j][1],
                            'version':'subbed'
                            })

            return self.sort_sources(sources_list)
