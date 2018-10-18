from anime_downloader import session
from anime_downloader.sites.kissanime import KissAnime
from anime_downloader.sites.anime import BaseEpisode, SearchResult
from anime_downloader.sites.exceptions import NotFoundError
from anime_downloader.const import desktop_headers, get_random_header

from bs4 import BeautifulSoup
import cfscrape
import logging

scraper = cfscrape.create_scraper()
session = session.get_session()


class KisscartoonEpisode(BaseEpisode):
    _base_url = ''
    VERIFY_HUMAN = False
    _episode_list_url = 'https://kisscartoon.ac/ajax/anime/load_episodes'
    QUALITIES = ['720p']

    def _get_sources(self):
        params = {
            'v': '1.1',
            'episode_id': self.url.split('id=')[-1],
        }
        headers = desktop_headers
        headers['referer'] = self.url
        res = session.get(self._episode_list_url, params=params, headers=headers)
        url = res.json()['value']

        headers = desktop_headers
        headers['referer'] = self.url
        res = session.get('https:' + url, headers=headers)

        return [(
            'no_extractor',
            res.json()['playlist'][0]['file']
        )]


class KissCartoon(KissAnime):
    sitename = 'kisscartoon'
    _episodeClass = KisscartoonEpisode

    @classmethod
    def search(cls, query):
        headers = get_random_header()
        headers['referer'] = 'http://kisscartoon.ac/'
        res = scraper.get(
            'http://kisscartoon.ac/Search/',
            params={
                's': query,
            },
            headers=headers,
        )
        logging.debug('Result url: {}'.format(res.url))

        soup = BeautifulSoup(res.text, 'html.parser')
        ret = []
        for res in soup.select_one('.listing').find_all('a'):
            res = SearchResult(
                title=res.text.strip('Watch '),
                url=res.get('href'),
                poster='',
            )
            logging.debug(res)
            ret.append(res)

        return ret

    def _scarpe_episodes(self, soup):
        ret = soup.find('div', {'class': 'listing'}).find_all('a')
        ret = [str(a['href']) for a in ret]

        if ret == []:
            err = 'No episodes found in url "{}"'.format(self.url)
            args = [self.url]
            raise NotFoundError(err, *args)

        return list(reversed(ret))
