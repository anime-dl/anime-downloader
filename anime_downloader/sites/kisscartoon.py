import cfscrape
from bs4 import BeautifulSoup
import logging
import requests

from anime_downloader.sites.kissanime import KissAnime
from anime_downloader.sites.anime import BaseEpisode, SearchResult
from anime_downloader.sites.exceptions import NotFoundError
from anime_downloader.const import desktop_headers, get_random_header

scraper = cfscrape.create_scraper(delay=10)

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
        res = requests.get(self._episode_list_url,
                           params=params, headers=headers)
        url = res.json()['value']

        headers = desktop_headers
        headers['referer'] = self.url
        res = requests.get('https:' + url, headers=headers)

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
        headers['referer'] = 'https://kisscartoon.ac'

        res = scraper.post(
            'https://kisscartoon.ac/Search/?s={}'.format(query),
            data={},
            headers=headers,
        )

        soup = BeautifulSoup(res.text, 'html.parser')

        results = soup.find_all('div', {'class' : 'item_movies_in_cat'})
        searched = [s for i, s in enumerate(results)]

        ret = []
        for res in searched:
            res = SearchResult(
                title=res.find('a').text,
                url=res.find('a').get('href'),
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
