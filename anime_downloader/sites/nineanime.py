from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites.exceptions import NotFoundError, AnimeDLError
from anime_downloader.sites import helpers
from anime_downloader import util
from anime_downloader.const import desktop_headers

from bs4 import BeautifulSoup

import logging

__all__ = ['NineAnimeEpisode', 'NineAnime']

logger = logging.getLogger(__name__)


class NineAnimeEpisode(AnimeEpisode, sitename='9anime'):
    _base_url = r'https://9anime.to/ajax/episode/info'
    ts = 0

    def _get_sources(self):
        servers = {
            'rapidvideo': '33',
            'streamango': '12',
            'mp4upload': '35',
        }
        server = self.config.get('server', 'mp4upload')
        params = {
            'id': self.url,
            'server': servers[server],
            'ts': self.ts
        }

        def get_stream_url(base_url, params, DD=None):
            params['_'] = int(generate_(params, DD=DD))
            data = helpers.get(base_url, params=params).json()

            return data['target']

        try:
            url = get_stream_url(self._base_url, params)
        except KeyError:
            try:
                del params['_']
                del params['ts']
                # I don't know if this is reliable or not.
                # For now it works.
                data = helpers.get(
                    'http://9anime.cloud/ajax/episode/info', params=params).json()
                url = data['target']
            except Exception as e:
                raise AnimeDLError(
                    '9anime probably changed their API again. Check the issues'
                    'here https://github.com/vn-ki/anime-downloader/issues. '
                    'If it has not been reported yet, please open a new issue'
                ) from e

        return [
            (server, url),
        ]


@helpers.not_working("9anime introduced captcha.")
class NineAnime(Anime, sitename='9anime'):
    """
    Site: 9anime

    Config
    ------
    server: One of ['rapidvideo', 'streamango']
        Selects the server.
    """
    sitename = '9anime'
    QUALITIES = ['360p', '480p', '720p', '1080p']

    @classmethod
    def search(cls, query):
        r = helpers.get('https://www4.9anime.to/search?', params={'keyword': query}, headers=desktop_headers)

        logger.debug(r.url)

        soup = BeautifulSoup(r.text, 'html.parser')

        search_results = soup.find(
            'div', {'class': 'film-list'}).find_all('div', {'class': 'item'})

        ret = []

        logger.debug('Search results')

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
            logger.debug(s)
            ret.append(s)

        return ret

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        ts = soup.find('html')['data-ts']
        NineAnimeEpisode.ts = ts
        logger.debug('data-ts: {}'.format(ts))

        # TODO: !HACK!
        # The below code should be refractored whenever I'm not lazy.
        # This was done as a fix to 9anime's switch to lazy loading of
        # episodes. I'm busy and lazy now, so I'm writing bad code.
        # Gomen'nasai
        api_url = "https://www8.9anime.to/ajax/film/servers/{}"
        api_url = api_url.format(self.url.rsplit('watch/', 1)[1].rsplit('.', 1)[1].split('/')[0])
        params = {}
        params['_'] = int(generate_(params))
        params['_'] = 648
        soup = helpers.soupify(helpers.get(api_url, params=params).json()['html'])
        episodes = soup.find('div', {'class': 'server', 'data-name': 33})
        episodes = episodes.find_all('li')

        if episodes == []:
            err = 'No episodes found in url "{}"'.format(self.url)
            args = [self.url]
            raise NotFoundError(err, *args)

        episode_ids = []

        for x in episodes:
            for a in x.find_all('a'):
                ep_id = a.get('data-id')
                episode_ids.append(ep_id)

        return episode_ids

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = str(soup.find('div', {'class': 'widget info'}).find(
            'h2', {'class': 'title'}).text)

        self.image = str(soup.find(
            'div', {'class': 'widget info'}).find('img')['src'])

        # self._len = int(soup.find_all(
            # 'ul', ['episodes'])[-1].find_all('a')[-1]['data-base'])

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
        DD = "e7b83f76"
    param_ = s(DD)

    for key, value in data.items():
        if DD == "e7b83f76":
            trans = a(DD + key, str(value))
        else:
            trans = a_old(DD + key, str(value))
        param_ += s(trans)

    return param_
