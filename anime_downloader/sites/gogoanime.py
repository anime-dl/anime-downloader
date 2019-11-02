import logging
import re

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from anime_downloader.sites.exceptions import AnimeDLError, NotFoundError

logger = logging.getLogger(__name__)


class GogoanimeEpisode(AnimeEpisode, sitename='gogoanime'):
    _base_url = 'https://www2.gogoanime.se'

    def _get_sources(self):

        # Scrape episode page to get link for download page
        soup = helpers.soupify(helpers.get(self.url))
        dl_page_url = []

        server = self.config.get('server', 'cdn')

        if server == 'cdn':
            # TODO: This should be a extractor class
            for element in soup.find_all('a', href=re.compile('https://vidstreaming\.io')):
                source_url = element.get('href')
                logger.debug('%s' % (source_url))
                dl_page_url = source_url
            # Scrape download page for default hoster (cdnfile) file link
            soup_cdnfile = helpers.soupify(helpers.get(dl_page_url))
            cdnfile_url = []

            for element in soup_cdnfile.find_all('a', href=re.compile('https://.*\.cdnfile\.info.*' + self.quality)):
                extractor_class = 'no_extractor'
                source_url = element.get('href')
                logger.debug('%s: %s' % (extractor_class, source_url))
                cdnfile_url.append((extractor_class, source_url,))
            return cdnfile_url

        else:
            soup = helpers.soupify(helpers.get(self.url))
            extractors_url = []

            for element in soup.select('.anime_muti_link > ul > li'):
                extractor_class = element.get('class')[0]
                source_url = element.a.get('data-video')
                logger.debug('%s: %s' % (extractor_class, source_url))
                # use mp4upload as source

                if extractor_class == 'mp4':
                    extractor_class = 'mp4upload'
                else:
                    raise AnimeDLError(
                        'No supported download servers found.  Try a different provider. '
                        'Check the issues here https://github.com/vn-ki/anime-downloader/issues. '
                    )
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
    _episode_list_url = 'https://www2.gogoanime.se//load-list-episode'
    _search_api_url = 'https://ajax.apimovie.xyz/site/loadAjaxSearch'

    @classmethod
    def search(cls, query):
        params = {
            'keyword': query,
            'id': -1,
            'link_web': 'https://www1.gogoanime.sh/'
        }
        soup = helpers.soupify(helpers.get(
            cls._search_api_url, params=params
        ).json()['content'])

        search_results = []

        for element in soup('a', class_='ss-title'):
            search_result = SearchResult(
                title=element.text,
                url=element.attrs['href'],
                poster=''
            )
            logger.debug(search_result)
            search_results.append(search_result)
        return search_results

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
            reversed(['https://www2.gogoanime.se'+a.get('href').strip()
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
