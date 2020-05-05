import logging
import re

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)

class Animedaisuki(Anime, sitename='animedaisuki'):
        sitename = 'animedaisuki'
        url = f'https://{sitename}.moe/browse'
        @classmethod
        def search(cls, query):
            search_results = helpers.soupify(helpers.get(cls.url, params={'q': query})).select('article > a')
            search_results = [
                SearchResult(
                    title=a.select('h3')[0].text,
                    url='https://animedaisuki.moe' + a.get('href'))
                for a in search_results
            ]
            return(search_results)

        def _scrape_episodes(self):
            soup = helpers.soupify(helpers.get(self.url))
            elements = soup.select('li.fa-play-circle > a')[::-1]
            return ['https://animedaisuki.moe' + a.get('href') for a in elements if a.get('href').startswith('/watch/')]

        def _scrape_metadata(self):
            soup = helpers.soupify(helpers.get(self.url))
            self.title = soup.select('h2.Title')[0].text

class AnimedaisukiEpisode(AnimeEpisode, sitename='animedaisuki'):
        def _get_sources(self):
            servers = self.config.get('servers',['no_extractor'])

            soup = helpers.soupify(helpers.get(self.url)).select('tbody a')
            captcha_regex = r'https://.*?s=(https.*)' #removes captcha redirect from link
            links = []

            website_extractors = [
            ['official','https://animedaisuki.moe/','no_extractor'],
            #['streamango','https://streamango.com/','streamango'], 
            #['openload','https://openload.co/','no_extractor'], both streamango and openload are dead
            ]

            for a in soup: #removes capcha from link
                if re.search(captcha_regex,a.get('href')):
                    links.append(re.search(captcha_regex,a.get('href')).group(1))
                else:
                    links.append(a.get('href'))
            
            logger.debug(links)

            for a in servers:
                for b in links:
                    for c in website_extractors:
                        if b.startswith(c[1]) and a == c[0]:
                            return [(c[2], b,)]
            
            logger.debug('No supported servers found')
            return ''
