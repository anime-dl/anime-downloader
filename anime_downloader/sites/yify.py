import requests, json, os
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from bs4 import BeautifulSoup
from io import StringIO

class Yify(Anime, sitename = 'yify'):
    sitename = 'yify'
    url = f'https://{sitename}.mx'
    @classmethod
    def search(cls, query):
        search_results = requests.get(f'https://yts.mx/ajax/search?query={query}').text
        io = StringIO(search_results)
        results = json.load(io)
        results_list = []
        for movie in results['data']:
            
            """
            TODO: Find a way to make quality selesction possible.
                  720p is 'modal-quality-720p'
                  1080p is 'modal-quality-1080p'
                  For now the default value is 720p.
            """
            html = BeautifulSoup(requests.get(movie['url']).text, 'html.parser')
            qq = html.find('div', id='modal-quality-720p').text
            get_magnet = html.find('div', id='modal-quality-720p').find_next('a', class_="magnet-download download-torrent magnet")['href']
            meta = {'year' : str(movie['year'])}
            title = movie['title']
            entry = [title, get_magnet, meta]
            results_list.append(entry)
        search_results = [
            SearchResult(
                title = results_list[i][0],
                url = results_list[i][1],
                meta= results_list[i][2])
            for i in range(len(results_list))
            ]
        return search_results
        
    def _scrape_episodes(self):
        return [self.url] #it is a magnet link, there is nothing else to change

class YifyMovie(AnimeEpisode, sitename='yify'):
    def _get_sources(self):
        return [('no_extractor', self.url)]
