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
            servers = self.config['servers']

            server_links = {
                'mp4upload':'https://www.mp4upload.com/embed-{}.html',
                'trollvid': 'https://trollvid.net/embed/{}',
                'mp4sh': 'https://mp4.sh/embed/{0}{1}',
                'vidstreaming':'https://vidstreaming.io/download?id={}'
            }

            soup = str(helpers.soupify(helpers.get(self.url)))
            x = re.search(r"xuath = '([^']*)", soup).group(1)
            episode_regex = r'var episode = (.*?});'
            api = json.loads(re.search(episode_regex,soup).group(1))
            slug = api['slug']
            sources = api['videos']

            try: #Continues even if vidstream api fails
                vidstream = helpers.get(f'https://vid.xngine.com/api/episode/{slug}',referer = self.url).json()
            except:
                vidstream = []
            
            for a in vidstream:
                if a['host'] == 'vidstreaming' and 'id' in a and 'type' in a:
                    sources.append(a)

            for a in servers: #trying all supported servers in order using the correct language
                for b in sources:
                    if b['type'] == version:
                        if b['host'] == a:
                            if get_extractor(a) == None:
                                continue
                            else:
                                provider = a[:]
                            embed = server_links.get(provider,'{}').format(b['id'],x)
                            return [(provider, embed,)]

            logger.debug('No servers found in selected language. Trying all supported servers')

            for a in servers: #trying all supported servers in order
                for b in sources:
                    if b['host'] == a:
                        if get_extractor(a) == None:
                            continue
                        else:
                            provider = a[:]
                        embed = server_links.get(provider,'{}').format(b['id'],x)
                        return [(provider, embed,)]

            logger.debug('No supported servers found, trying mp4sh')

            if re.search(r'"trollvid","id":"([^"]*)', soup):
                token = re.search(r'"trollvid","id":"([^"]*)', soup).group(1)
                embed = server_links.get('mp4sh','{}').format(token,x)
                return [('mp4sh', embed,)]
            else:
                logger.debug('No servers found')
                return [('no_extractor', '',)]
