import logging
import re
import json
from anime_downloader.extractors import get_extractor
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)

class Dubbedanime(Anime, sitename='dubbedanime'):
        sitename = 'dubbedanime'
        url = f'https://{sitename}.net'
        @classmethod
        def search(cls, query):
            search_results = helpers.post(f'https://ww5.dubbedanime.net/ajax/paginate',
            data={
                'query[search]': query,
                'what': 'query',
                'model': 'Anime',
                'size': 30,
                'letter': 'all',
            }).json()
            search_results = [
                SearchResult(
                    title=search_results['results'][a]['title'],
                    url=cls.url + search_results['results'][a]['url'])
                for a in range(len(search_results['results']))
            ]
            return(search_results)

        def _scrape_episodes(self):
            soup = helpers.soupify(helpers.get(self.url))
            elements = soup.find("ul", {"id": "episodes-grid"}).select('li > div > a')
            return [('https://dubbedanime.net' + a.get('href')) for a in elements[::-1]]

        def _scrape_metadata(self):
            soup = helpers.soupify(helpers.get(self.url))
            self.title = soup.select('h1.h3')[0].text

class DubbedanimeEpisode(AnimeEpisode, sitename='dubbedanime'):
        def _get_sources(self):
            version = self.config['version']
            server = self.config['server']
            fallback = self.config['fallback_servers']

            server_links = {
                'mp4upload':'https://www.mp4upload.com/embed-{}.html',
                'trollvid': 'https://trollvid.net/embed/{}',
                'mp4sh': 'https://mp4.sh/embed/{0}{1}',
            }

            soup = str(helpers.soupify(helpers.get(self.url)))
            x = re.search(r"xuath = '([^']*)", soup).group(1)
            episode_regex = r'var episode = ({[^;]*)'
            sources = json.loads(re.search(episode_regex,soup).group(1))['videos']

            for a in sources: #Testing sources with selected language and provider
                if a['type'] == version:
                    if a['host'] == server:
                        if get_extractor(server) == None:
                            continue
                        else:
                            provider = server[:]

                        embed = server_links.get(provider,'{}').format(a['id'],x)
                        return [(provider, embed,)]

            logger.debug('Preferred server %s not found in selected language. Trying all supported servers in selected language.',server)

            for a in fallback: #Testing sources with selected language
                for b in sources: 
                    if b['type'] == version:
                        if b['host'] == a:
                            if get_extractor(a) == None:
                                continue
                            else:
                                provider = a[:]
                            
                            embed = server_links.get(provider,'{}').format(b['id'],x)
                            return [(provider, embed,)]

            logger.debug('No %s servers found, trying all supported servers.',version)
            
            for a in fallback: #Testing all sources
                for b in sources: 
                    if b['host'] == a:
                        if get_extractor(a) == None:
                            continue
                        else:
                            provider = a[:]
                        
                        embed = server_links.get(provider,'{}').format(b['id'],x)
                        return [(provider, embed,)]

            return [('no_extractor', '',)]
