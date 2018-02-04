import requests
from bs4 import BeautifulSoup
import json


QUALITIES = ['360p', '480p', '720p']


class AnimeDLError(Exception):
    pass


class URLError(AnimeDLError):
    pass


class NotFoundError(AnimeDLError):
    pass


class Anime:
    def __init__(self, url, quality='720p'):

        if quality not in QUALITIES:
            raise AnimeDLError('Incorrect quality: "{}"'.format(quality))

        self.url = url
        self.quality = quality
        self.getEpisodes()

    def getEpisodes(self):
        self._episodeIds = []
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        episodes = soup.find_all('ul', ['episodes'])
        episodes = episodes[:int(len(episodes)/3)]

        for x in episodes:
            for a in x.find_all('a'):
                ep_id = a.get('data-id')
                self._episodeIds.append(ep_id)

    def __len__(self):
        return len(self._episodeIds)

    def __getitem__(self, index):
        ep_id = self._episodeIds[index]
        return Episode(ep_id, self.quality)


class Episode:
    _base_url = r'https://9anime.is/ajax/episode/info?id={0}&server=33'

    def __init__(self, episode_id, quality='720p'):

        if quality not in QUALITIES:
            raise AnimeDLError('Incorrect quality: "{}"'.format(quality))

        self.episode_id = episode_id
        self.quality = quality
        self.getData()

    def getData(self):
        url = self._base_url.format(self.episode_id)
        data = json.loads(requests.get(url).text)
        url = data.get('target')
        r = requests.get(url+'&q='+self.quality)
        soup = BeautifulSoup(r.text, 'html.parser')
        try:
            self.stream_url = soup.find_all('source')[0].get('src')
        except IndexError:
            raise NotFoundError("Episode not found")

    def download():
        pass
