from anime_downloader.sites.anime import BaseAnime, BaseEpisode, SearchResult
from anime_downloader.sites.exceptions import AnimeDLError, URLError, NotFoundError


import json
import requests
from bs4 import BeautifulSoup

import re
import time

import logging


__all__ = ['NineAnimeEpisode', 'NineAnime']

class NineAnimeEpisode(BaseEpisode):
    QUALITIES = ['360p', '480p', '720p']
    _base_url = r'https://9anime.is/ajax/episode/info?id={id}&server={server}&_={param_}&ts={ts}'
    ts = 0

    def getData(self):
        params = {
            'id': self.episode_id,
            'server': '33',
            'ts': self.ts
        }
        params['param_'] = int(generate_(params))

        logging.debug('API call params: {}'.format(params))

        url = self._base_url.format(**params)

        logging.debug('API call URL: {}'.format(url))

        data = json.loads(requests.get(url).text)

        logging.debug('Returned data: {}'.format(data))

        url = data['target']
        title_re = re.compile(r'"og:title" content="(.*)"')
        image_re = re.compile(r'"og:image" content="(.*)"')

        r = requests.get(url+'&q='+self.quality)
        soup = BeautifulSoup(r.text, 'html.parser')
        try:
            self.stream_url = soup.find_all('source')[0].get('src')
        except IndexError:
            raise NotFoundError("Episode not found")
        try:
            self.title = title_re.findall(r.text)[0]
            self.image = image_re.findall(r.text)[0]
        except Exception as e:
            logging.debug(e)
            pass



class NineAnime(BaseAnime):
    sitename = '9Anime'
    QUALITIES = ['360p', '480p', '720p']
    _episodeClass = NineAnimeEpisode

    @classmethod
    def search(cls, query):
        r = requests.get('https://www4.9anime.is/search?',
                         params={'keyword': query})

        logging.debug(r.url)

        soup = BeautifulSoup(r.text, 'html.parser')

        # 9anime has search result in
        # <div class="item">
        #   <div class="inner">
        #    <a href="https://www4.9anime.is/watch/dragon-ball-super.7jly"
        #       class="poster tooltipstered" data-tip="ajax/film/tooltip/7jly?5827f020">
        #       <img src="http://static.akacdn.ru/static/images/2018/03/43012fe439631a2cecfcf248841e15f7.jpg"
        #            alt="Dragon Ball Super">
        #       <div class="status">
        #           <span class="bar">
        #           </span>
        #           <div class="ep"> Ep 131/131 </div>
        #       </div>
        #     </a>
        #    <a href="https://www4.9anime.is/watch/dragon-ball-super.7jly"
        #      data-jtitle="Dragon Ball Super"
        #      class="name">
        #           Dragon Ball Super
        #    </a>
        #   </div>
        # </div>

        search_results = soup.find(
            'div', {'class': 'film-list'}).find_all('div', {'class': 'item'})

        ret = []

        logging.debug('Search results')

        for item in search_results:
            s = SearchResult(
                title=item.find('a', {'class': 'name'}).contents[0],
                url=item.find('a')['href'],
                poster=item.find('img')['src']
            )
            logging.debug(s)
            ret.append(s)

        return ret

    def _getEpisodeUrls(self, soup):
        ts = soup.find('html')['data-ts']
        self._episodeClass.ts = ts
        logging.debug('data-ts: {}'.format(ts))

        episodes = soup.find_all('ul', ['episodes'])

        if episodes == []:
            err = 'No episodes found in url "{}"'.format(self.url)
            args = [self.url]
            raise NotFoundError(err, *args)

        servers = soup.find_all('span', {'class': 'tab'})[:-3]

        episodes = episodes[:int(len(episodes)/len(servers))]

        episode_ids = []

        for x in episodes:
            for a in x.find_all('a'):
                ep_id = a.get('data-id')
                episode_ids.append(ep_id)

        return episode_ids

    def _getMetadata(self, soup):
        title = soup.find_all('h1', {'class': 'title'})
        self.title = title[0].contents[0]
        self._len = int(soup.find_all(
            'ul', ['episodes'])[-1].find_all('a')[-1]['data-base'])


def s(t):
    i = 0
    for (idx, char) in enumerate(t):
        i += ord(char) + idx

    return i


def a(t, e):
    n = sum(ord(c) for c in t) + sum(ord(c) for c in e)
    return hex(n)[2:]


def generate_(data):
    DD = "iQDWcsGqN"
    param_ = s(DD)

    for key, value in data.items():
        trans = a(DD + key, str(value))
        param_  += s(trans)


    return param_
