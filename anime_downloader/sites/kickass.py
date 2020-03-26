import logging
import re
import json

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

class KickAss(Anime, sitename='kickassanime'):
        sitename = 'kickassanime'
        url = f'https://{sitename}.rs/search'

        @classmethod
        def search(cls, query):
            search_results = helpers.soupify(helpers.get(cls.url,
                                         params={'q': query}))
            regex = r'\[{[\W\w]*?}]'
            search_results = json.loads(re.search(regex,str(search_results)).group())

            title_data = {'data' : []}
            for a in search_results:
                data = {
                    'url' : f'https://kickassanime.rs{a["slug"]}',
                    'title' : a['name'],
                }
                title_data['data'].append(data)

            search_results = [
                SearchResult(
                    title=result["title"],
                    url=result["url"])
                for result in title_data.get('data', [])
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
            
class KickAssEpisode(AnimeEpisode, sitename='kickassanime'):
        def _get_sources(self):
            soup = helpers.soupify(helpers.get(self.url))
            regex = r'{"clip[\w\W]*?}\]} '
            elements = json.loads(re.search(regex,str(soup)).group())
            links = ['link1','link2','link3','link4']
            sources_list = [] #Primary sources which links to more sources
            for a in links:
                if len((elements['episode'][a]).replace(' ','')) != 0:
                    sources_list.append(elements['episode'][a])

            soup = helpers.get(sources_list[0]).text
            regex = r'\[{[\W\w]*?}\]'
            sources = re.search(regex,str(soup))
            
            if not sources: #Either vidstream or haloani
                regex = r"[^/]window\.location = '[^']*"
                sources = re.search(regex,str(soup)).group()[20:]
                return [('vidstream', sources,)]

            sources = json.loads(sources.group())
            return [('haloani', sources[0]['src'],)]