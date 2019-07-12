from anime_downloader.sites.kissanime import KissAnime
from anime_downloader.sites.anime import AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from anime_downloader.sites.exceptions import NotFoundError

import logging


logger = logging.getLogger(__name__)


class KisscartoonEpisode(AnimeEpisode, sitename='kisscartoon'):
    _base_url = ''
    VERIFY_HUMAN = False
    _episode_list_url = 'https://kisscartoon.is/ajax/anime/load_episodes'
    QUALITIES = ['720p']

    def _get_sources(self):
        params = {
            'v': '1.1',
            'episode_id': self.url.split('id=')[-1],
        }
        url = helpers.get(self._episode_list_url,
                          params=params,
                          referer=self.url).json()['value']

        res = helpers.get('https:' + url, referer=self.url)

        return [(
            'no_extractor',
            res.json()['playlist'][0]['file']
        )]


class KissCartoon(KissAnime, sitename='kisscartoon'):
    sitename='kisscartoon'

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.get(
            'https://kisscartoon.is/Search/',
            params=dict(s=query),
            referer='https://kisscartoon.is/',
        ))

        ret = []
        for res in soup.select('.listing a'):
            res = SearchResult(
                title=res.text.strip('Watch '),
                url=res.get('href'),
                poster='',
            )
            logger.debug(res)
            ret.append(res)

        return ret

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        ret = [str(a['href'])
               for a in soup.select('.listing a')]

        if ret == []:
            err = 'No episodes found in url "{}"'.format(self.url)
            args = [self.url]
            raise NotFoundError(err, *args)

        return list(reversed(ret))
