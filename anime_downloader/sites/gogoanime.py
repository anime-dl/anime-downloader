import logging
import re

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)


class GogoanimeEpisode(AnimeEpisode, sitename='gogoanime'):
    _base_url = 'https://gogoanime.io/'

    def _get_sources(self):
        # Scrape episode page to get link for download page
        soup = helpers.soupify(helpers.get(self.url))
        dl_page_url = []

        server = self.config.get('server', 'cdn')
        if server == 'cdn':
            for element in soup.find_all('a', href=re.compile('https://vidstreaming\.io')):
                source_url = element.get('href')
                logger.debug('%s' % (source_url))
                dl_page_url = source_url
                return[('vidstream',source_url)]

        else:
            soup = helpers.soupify(helpers.get(self.url))
            extractors_url = []

            for element in soup.select('.anime_muti_link > ul > li'):
                extractor_class = element.get('class')[0]
                source_url = element.a.get('data-video')
                logger.debug('%s: %s' % (extractor_class, source_url))
                # prefer streamango, else use mp4upload and rapidvideo as sources

                if extractor_class == 'streamango':
                    extractor_class = 'streamango'
                elif extractor_class == 'mp4':
                    extractor_class = 'mp4upload'
                elif extractor_class != 'rapidvideo':
                    continue
                logger.debug('%s: %s' % (extractor_class, source_url))
                extractors_url.append((extractor_class, source_url,))
            return extractors_url


class GogoAnime(Anime, sitename='gogoanime'):
    """
    Nice things

    Siteconfig
    ----------

    server: one of below
        cdn, others: cdn uses gogoanime cdn, others will use streamango, mp4upload or rapidvideo in that order.

    """
    sitename = 'gogoanime'
    QUALITIES = ['360p', '480p', '720p', '1080p']
    _base_url = 'https://gogoanime.io/'
    _episode_list_url = 'https://gogoanime.io/load-list-episode'
    _search_url = 'https://gogoanime.io/search.html'
    @classmethod
    def search(cls, query):
        search_results = helpers.soupify(helpers.get(cls._search_url, params = {'keyword': query}))
        search_results = search_results.select('ul.items > li > p > a')

        search_results = [
            SearchResult(
                title=a.get('title'),
                url='https://gogoanime.io' + a.get('href'))
            for a in search_results
        ]
        return(search_results)

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        anime_id = soup.select_one('input#movie_id').attrs['value']
        params = {
            'default_ep': 0,
            'ep_start': 0,
            'ep_end': 999999,  # Using a very big number works :)
            'id': anime_id,
        }

        soup = helpers.soupify(helpers.get(self._episode_list_url,
                                           params=params))

        epurls = list(
            reversed([self._base_url + a.get('href').strip()
                      for a in soup.select('li a')])
        )

        return epurls

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        meta = soup.select_one('.anime_info_body_bg')
        self.title = meta.find('h1').text
        self.poster = meta.find('img').get('src')

        metdata = {}
        for elem in meta.find_all('p'):
            try:
                key, val = [v.strip(' :')
                            for v in elem.text.strip().split('\n')]
            except Exception:
                continue
            metdata[key] = val

        self.meta = metdata
