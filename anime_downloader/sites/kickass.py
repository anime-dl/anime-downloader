import logging
import re
import json

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)

class KickAss(Anime, sitename='kickass'):
        sitename = 'kickass'
        url = f'https://kickassanime.rs/search'

        @classmethod
        def search(cls, query):
            search_results = helpers.soupify(helpers.get(cls.url,
                                         params={'q': query}))
            regex = r'\[{[\W\w]*?}]'
            search_results = json.loads(re.search(regex,str(search_results)).group())

            search_results = [
                SearchResult(
                    title=a['name'],
                    url=f'https://kickassanime.rs{a["slug"]}')
                for a in search_results
            ]
            return(search_results)

        def _scrape_episodes(self):
            soup = helpers.soupify(helpers.get(self.url))
            
            regex = r'\[{[\W\w]*?}]'
            episodes = json.loads(re.search(regex,str(soup)).group())

            return [f'https://kickassanime.rs{a["slug"]}' for a in episodes[::-1]]

        def _scrape_metadata(self):
            soup = helpers.get(self.url).text
            
            regex = r'{"name"[^}]*}'
            info = json.loads(re.search(regex,str(soup)).group()+']}')
            self.title = info['name']
            
class KickAssEpisode(AnimeEpisode, sitename='kickass'):
        def _get_sources(self):
            server = self.config['server']
            fallback = self.config['fallback_servers']
            ext_fallback = self.config['ext_fallback_servers']

            soup = helpers.soupify(helpers.get(self.url))
            regex = r'{"clip[\w\W]*?}\]} '
            elements = json.loads(re.search(regex,str(soup)).group())
            links = ['link1','link2','link3','link4']
            sources_list = [] #Primary sources which links to more sources
            ext_servers = []
            for a in links:
                if len((elements['episode'][a]).replace(' ','')) != 0:
                    sources_list.append(elements['episode'][a])
            if elements['ext_servers']:
                for a in elements['ext_servers']:
                    ext_servers.append(a)
            soup = helpers.get(sources_list[0]).text
            regex = r'\[{[\W\w]*?}\]'
            sources = re.search(regex,str(soup))

            if not sources:
                regex = r"[^/]window\.location = '([^']*)"
                sources = re.search(regex,str(soup))
                if sources:
                    return [('vidstream', sources.group(1),)]
                else:
                    if len(ext_servers) == 0:
                        return ''
                    for i in range(2):
                        for a in ext_servers:
                            if a in ext_fallback or i == 1:
                                if a['name'] == 'Vidstreaming' or a['name'] == 'Vidcdn':
                                    return [('vidstream', a['link'],)]
                                else:
                                    return [('haloani', a['link'],)]

            sources = json.loads(sources.group())
            for i in range(3):
                if i == 1:logger.debug('Preferred server "%s" not found. Trying all supported servers.',self.config['server'])
                if i == 2:logger.warning('No supported servers found. Trying all servers. This will most likely not work')
                for a in sources:
                    if i == 1:
                        for b in fallback:
                            if a['name'] == b:
                                return [('haloani', a['src'],)]
                    if a['name'] == self.config['server'] or i == 2:
                        return [('haloani', a['src'],)]
