import logging
import re
import sys
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

class WatchMovie(Anime, sitename='watchmovie'):
        sitename = 'watchmovie'
        url = f'https://{sitename}.movie'
        @classmethod
        def search(cls, query):
            search_results = helpers.soupify(helpers.get(cls.url+'/search.html',params={'keyword': query})).select('a.videoHname')
            
            search_results = [
                SearchResult(
                    title=a.get('title'),
                    url=cls.url+a.get('href'))
                for a in search_results
            ]
            return(search_results)

        def _scrape_episodes(self):
            url = self.url+'/season'
            soup = helpers.soupify(helpers.get(url)).select('a.videoHname')
            return ['https://watchmovie.movie'+a.get('href') for a in soup[::-1]]

        def _scrape_metadata(self):
            self.title = helpers.soupify(helpers.get(self.url)).select('div.page-title > h1')[0].text
            
class WatchMovieEpisode(AnimeEpisode, sitename='watchmovie'):
        def _get_sources(self):
            soup = helpers.soupify(helpers.get(self.url))
            test = soup.select('div.anime_muti_link > ul > li > a')
            for a in test:
                url = a.get('data-video')
                if 'fembed' in url or 'gcloud' in url:
                    return[('gcloud',url)]