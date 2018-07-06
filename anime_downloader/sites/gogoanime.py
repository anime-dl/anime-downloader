from anime_downloader.sites.anime import BaseAnime, BaseEpisode
import requests
import re
from bs4 import BeautifulSoup


class GogoanimeEpisode(BaseEpisode):
    QUALITIES = ['360p', '480p', '720p']
    _base_url = 'https://www2.gogoanime.se'

    def _get_sources(self):
        soup = BeautifulSoup(requests.get(self.url).text, 'html.parser')
        url = 'https:'+soup.select_one('li.anime a').get('data-video')

        res = requests.get(url)
        ep_re = re.compile(r"file:.*?'(.*?)'")

        stream_urls = ep_re.findall(res.text)
        return [('no_extractor', url) for url in stream_urls]


class GogoAnime(BaseAnime):
    sitename = 'gogoanime'
    QUALITIES = ['360p', '480p', '720p']
    _episode_list_url = 'https://www2.gogoanime.se//load-list-episode'
    _episodeClass = GogoanimeEpisode

    def _scarpe_episodes(self, soup):
        anime_id = soup.select_one('input#movie_id').attrs['value']
        params = {
            'default_ep': 0,
            'ep_start': 0,
            'ep_end': 999999,  # Using a very big number works :)
            'id': anime_id,
        }

        res = requests.get(self._episode_list_url, params=params)
        soup = BeautifulSoup(res.text, 'html.parser')

        epurls = list(
            reversed(['https://www2.gogoanime.se'+a.get('href').strip()
                      for a in soup.select('li a')])
        )

        return epurls

    def _scrape_metadata(self, soup):
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
