from .anime import BaseAnime, BaseEpisode, AnimeDLError, URLError, NotFoundError
import json
import requests
from bs4 import BeautifulSoup
import json
import re
import time


class NineAnimeEpisode(BaseEpisode):
    QUALITIES = ['360p', '480p', '720p']
    _base_url = r'https://9anime.is/ajax/episode/info?id={id}&server={server}&_={param_}&ts={ts}'
    ts = 0

    def getData(self):
        params = {
            'id': self.episode_id,
            'server': '33',
            # 'update': 0,
            'ts': self.ts
        }
        params['param_'] = int(generate_(params))
        url = self._base_url.format(**params)

        data = json.loads(requests.get(url).text)
        url = data['target']
        title_re = re.compile(r'"og:title" content="(.*)"')
        image_re = re.compile(r'"og:image" content="(.*)"')

        r = requests.get(url+'&q='+self.quality)
        soup = BeautifulSoup(r.text, 'html.parser')
        try:
            self.stream_url = soup.find_all('source')[0].get('src')
            self.title = title_re.findall(r.text)[0]
            self.image = image_re.findall(r.text)[0]
        except IndexError:
            raise NotFoundError("Episode not found")



class NineAnime(BaseAnime):
    QUALITIES = ['360p', '480p', '720p']
    _episodeClass = NineAnimeEpisode

    def _getEpisodeUrls(self, soup):
        ts = soup.find('html')['data-ts']
        self._episodeClass.ts = ts
        episodes = soup.find_all('ul', ['episodes'])
        if episodes == []:
            err = 'No episodes found in url "{}"'.format(self.url)
            if self._callback:
                self._callback(err)
            args = [self.url]
            raise NotFoundError(err, *args)
        episodes = episodes[:int(len(episodes)/3)]

        for x in episodes:
            for a in x.find_all('a'):
                ep_id = a.get('data-id')
                self._episodeIds.append(ep_id)


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
