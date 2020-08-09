import logging
import re

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)

class VoirAnime(Anime, sitename='voiranime'):
        sitename = 'voiranime'
        url = f'https://{sitename}.com/'
        @classmethod
        def search(cls, query):
            search_results = helpers.soupify(helpers.get(cls.url, params={'s': query})).select('div.item-head > h3 > a')
            search_results = [
                SearchResult(
                    title=i.text,
                    url=i.get('href'))
                for i in search_results
            ]
            return search_results


        def _scrape_episodes(self):
            soup = helpers.soupify(helpers.get(self.url))
            next_page = soup.select('a.ct-btn')[0].get('href')
            soup = helpers.soupify(helpers.get(next_page))
            episodes = soup.select('ul.video-series-list > li > a.btn-default')
            return [i.get('href') for i in episodes]


        def _scrape_metadata(self):
            soup = helpers.soupify(helpers.get(self.url))
            self.title = soup.select('div.container > h1')[0].text


class VoirAnimeEpisode(AnimeEpisode, sitename='voiranime'):
        def _get_sources(self):
            soup = helpers.soupify(helpers.get(self.url))
            """These could probably be condensed down to one, but would look too spooky"""
            multilinks_regex = r'var\s*multilinks\s*=\s*\[\[{(.*?)}]];'
            mutilinks_iframe_regex = r"iframe\s*src=\\(\"|')([^(\"|')]*)"
            multilinks = re.search(multilinks_regex, str(soup)).group(1)
            logger.debug('Multilinks: {}'.format(multilinks))
            iframes = re.findall(mutilinks_iframe_regex,multilinks)
            logger.debug('Iframes: {}'.format(iframes))
            sources = [i[-1].replace('\\','') for i in iframes]
            
            extractors = { 
            #url                           #Extractor    #Server in config
            'https://gounlimited.to/embed':['mp4upload','gounlimited'],
            }

            sources_list = []
            for i in sources:
                for j in extractors:
                    if j in i:
                        sources_list.append({
                            'extractor':extractors[j][0],
                            'url':i,
                            'server':extractors[j][1],
                            'version':'subbed'
                            })

            return self.sort_sources(sources_list)
