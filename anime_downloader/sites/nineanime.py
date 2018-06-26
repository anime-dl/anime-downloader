from anime_downloader.sites.anime import BaseAnime, BaseEpisode, SearchResult
from anime_downloader.sites.exceptions import NotFoundError, AnimeDLError
from anime_downloader.sites import util
from anime_downloader.const import desktop_headers

import requests
from bs4 import BeautifulSoup

import logging

__all__ = ['NineAnimeEpisode', 'NineAnime']


class NineAnimeEpisode(BaseEpisode):
    QUALITIES = ['360p', '480p', '720p', '1080p']
    _base_url = r'https://9anime.is/ajax/episode/info'
    ts = 0

    def get_data(self):
        params = {
            'id': self.episode_id,
            'server': '33',
            'ts': self.ts
        }

        def get_stream_url(base_url, params, DD=None):
            params['_'] = int(generate_(params, DD=DD))
            data = util.get_json(base_url, params=params)

            return data['target']

        try:
            url = get_stream_url(self._base_url, params)
        except KeyError:
            try:
                del params['_']
                del params['ts']
                # I don't know if this is reliable or not.
                # For now it works.
                data = util.get_json(
                    'http://9anime.cloud/ajax/episode/info', params=params)
                url = data['target']
            except Exception as e:
                raise AnimeDLError(
                    '9anime probably changed their API again. Check the issues'
                    'here https://github.com/vn-ki/anime-downloader/issues. '
                    'If it has not been reported yet, please open a new issue'
                ) from e

        headers = desktop_headers
        headers['referer'] = 'www5.9anime.is'

        data = util.get_stream_url_rapidvideo(url, self.quality, headers)

        self.stream_url = data['stream_url']
        self.title = data['title']
        self.image = data['image']


class NineAnime(BaseAnime):
    sitename = '9anime'
    QUALITIES = ['360p', '480p', '720p', '1080p']
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
            meta = dict()
            m = item.find('div', {'class': 'status'})
            for item in m.find_all('div'):
                meta[item.attrs['class'][0]] = item.text.strip()
            s.meta = meta
            logging.debug(s)
            ret.append(s)

        return ret

    def _scarpe_episodes(self, soup):
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

    def _scrape_metadata(self, soup):
        self.title = str(soup.find('div', {'class': 'widget info'}).find(
            'h2', {'class': 'title'}).text)

        self.image = str(soup.find(
            'div', {'class': 'widget info'}).find('img')['src'])

        self._len = int(soup.find_all(
            'ul', ['episodes'])[-1].find_all('a')[-1]['data-base'])

        meta1 = soup.find('div', {'class': 'widget info'}).find_all('dl')[0]
        meta2 = soup.find('div', {'class': 'widget info'}).find_all('dl')[1]
        dd = meta1.find_all('dd') + meta2.find_all('dd')
        dt = meta1.find_all('dt') + meta2.find_all('dt')
        self.meta = dict(
            zip([tag.text.strip(': ') for tag in dt],
                [tag.text.strip() for tag in dd])
        )


def s(t):
    i = 0
    for (idx, char) in enumerate(t):
        i += ord(char) + idx

    return i


def a(t, e):
    n = 0
    for i in range(max(len(t), len(e))):
        n *= ord(e[i]) if i < len(e) else 8
        n *= ord(t[i]) if i < len(t) else 8
    return hex(n)[2:]


def a_old(t, e):
    n = 0
    for i in range(max(len(t), len(e))):
        n += ord(e[i]) if i < len(e) else 0
        n += ord(t[i]) if i < len(t) else 0
    return hex(n)[2:]


def generate_(data, DD=None):
    if DD is None:
        DD = "bfcad671"
    param_ = s(DD)

    for key, value in data.items():
        if DD == "bfcad671":
            trans = a(DD + key, str(value))
        else:
            trans = a_old(DD + key, str(value))
        param_ += s(trans)

    return param_
