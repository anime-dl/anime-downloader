from anime_downloader.sites.kissanime import Kissanime
from anime_downloader.sites.anime import BaseEpisode
from anime_downloader.sites.exceptions import NotFoundError

import requests


class KisscartoonEpisode(BaseEpisode):
    _base_url = ''
    VERIFY_HUMAN = False
    _api_url = 'https://kisscartoon.ac/ajax/anime/load_episodes?v=1.1&episode_id={}'
    QUALITIES = ['720p']

    def getData(self):
        ep_id = self.episode_id.split('id=')[-1]
        url = self._api_url.format(ep_id)
        res = requests.get(url)
        url = res.json()['value']

        headers = {'referer': self.episode_id}
        res = requests.get('https:' + url, headers=headers)

        self.stream_url = res.json()['playlist'][0]['file']
        self.title = self.episode_id.split(
            'Cartoon/')[-1].split('.')[0] + self.episode_id.split(
                'Episode')[-1].split('?')[0]


class Kisscarton(Kissanime):
    sitename = 'kisscartoon'
    _episodeClass = KisscartoonEpisode

    def _getEpisodeUrls(self, soup):
        ret = soup.find('div', {'class': 'listing'}).find_all('a')
        ret = [str(a['href']) for a in ret]

        if ret == []:
            err = 'No episodes found in url "{}"'.format(self.url)
            args = [self.url]
            raise NotFoundError(err, *args)

        return list(reversed(ret))
