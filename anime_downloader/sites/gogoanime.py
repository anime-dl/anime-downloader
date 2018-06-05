from anime_downloader.sites.anime import BaseAnime, BaseEpisode
import requests
import re
from bs4 import BeautifulSoup


class GogoanimeEpisode(BaseEpisode):
    QUALITIES = ['360p', '480p', '720p']
    _base_url = 'https://www2.gogoanime.se'

    def getData(self):
        url = self._base_url + self.episode_id
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        url = 'https:'+soup.select_one('li.anime a').get('data-video')

        res = requests.get(url)
        ep_re = re.compile(r"file:.*?'(.*?)'")

        self._stream_urls = ep_re.findall(res.text)
        self.stream_url = self._stream_urls[0]


class Gogoanime(BaseAnime):
    sitename = 'gogoanime'
    QUALITIES = ['360p', '480p', '720p']
    _api_url = 'https://www2.gogoanime.se//load-list-episode?ep_start=1&'\
               'ep_end={ep_end}&id={id}&default_ep=0'
    _episodeClass = GogoanimeEpisode

    def _getEpisodeUrls(self, soup):
        ep_end = max([int(a.attrs['ep_end'])
                     for a in soup.find(
                         'ul', {'id': 'episode_page'}
                     ).find_all('a')])

        id = soup.find('input', {'id': 'movie_id'}).attrs['value']

        url = self._api_url.format(id=id, ep_end=ep_end)
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')

        epurls = list(reversed([a.get('href').strip()
                                for a in soup.select('li a')]))

        return epurls

    def _getMetadata(self, soup):
        meta = soup.find('div', {'class': 'anime_info_body_bg'})
        self.title = meta.find('h1').text
        self.poster = meta.find('img').get('src')

        metdata = {}
        for elem in meta.find_all('p'):
            try:
                key, val = [v.strip(' :') for v in elem.text.strip().split('\n')]
            except Exception:
                continue
            metdata[key] = val

        self.meta = metdata
