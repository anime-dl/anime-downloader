import logging
import re
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)

class VidStream(Anime, sitename='vidstream'):
        sitename = 'vidstream'
        @classmethod
        def search(cls, query):
            """
            #Use below code for live ajax search.
            #Will show max 10 search results

            search_results = helpers.get('https://vidstreaming.io/ajax-search.html', 
                params = {'keyword': query},
                headers = {
                    'X-Requested-With':'XMLHttpRequest',
                }
            ).json()
            search_results = helpers.soupify(search_results['content']).select('li > a')
            return [
                SearchResult(
                    title=i.text,
                    url=f"https://vidstreaming.io{i.get('href')}")
                for i in search_results
            ]
            """
            # Only using page 1, resulting in max 30 results
            # Very few shows will get impacted by this
            search_results = helpers.soupify(helpers.get('https://vidstreaming.io/search.html', 
                params = {'keyword':query})
            ).select('ul.listing > li.video-block > a')
            # Regex to cut out the "Episode xxx"
            return [
                SearchResult(
                    title=re.sub(r"(E|e)pisode\s*[0-9]*", '', i.select('div.name')[0].text.strip()),
                    url=f"https://vidstreaming.io{i.get('href')}")
                for i in search_results
            ]


        def _scrape_episodes(self):
            soup = helpers.soupify(helpers.get(self.url))
            elements = soup.select('div.video-info-left > ul.listing > li.video-block > a')
            return [f"https://vidstreaming.io{i.get('href')}" for i in elements[::-1]]


        def _scrape_metadata(self):
            soup = helpers.soupify(helpers.get(self.url))
            self.title = soup.select('span.date')[0].text.strip()


class VidStreamEpisode(AnimeEpisode, sitename='vidstream'):
        def _get_sources(self):
            soup = helpers.soupify(helpers.get(self.url))
            iframes = soup.select('iframe')
            logger.debug('Iframes: {}'.format(iframes))
            for i in iframes:
                # Simple check in case there's advertising iframes.
                if 'streaming.php' in i.get('src'):
                    return [('vidstream', i.get('src'),)]
            
            return ''
