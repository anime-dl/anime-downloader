import re

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

class Nyaa(Anime, sitename = 'nyaa'):
    sitename = 'nyaa'
    url = f'https://{sitename}.si'
    @classmethod
    def search(cls,query):
        rex = r'(magnet:)+[^"]*'
        search_results = helpers.soupify(helpers.get(f"https://nyaa.si/?f=2&c=1_2&q={query}&s=size&o=desc"))
        
        search_results = [
            SearchResult(
                title = i.select("a:not(.comments)")[1].get("title") + ' | '+ i.find_all('td',class_ = 'text-center')[1].text,
                url = i.find_all('a',{'href':re.compile(rex)})[0].get('href'))
            for i in search_results.select("tr.default,tr.success")
            ]

        return search_results
        
    def _scrape_episodes(self):
        return [self.url] #the magnet has all episodes making this redundant

class NyaaEpisode(AnimeEpisode, sitename='nyaa'):
    def _get_sources(self):
        return [('no_extractor', self.url,)]
