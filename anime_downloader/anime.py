import requests
from bs4 import BeautifulSoup
import json
import re
import time
import sys


QUALITIES = ['360p', '480p', '720p']


class AnimeDLError(Exception):
    pass


class URLError(AnimeDLError):
    pass


class NotFoundError(AnimeDLError):
    pass


class Anime:
    def __init__(self, url, quality='720p', callback=None):

        if quality not in QUALITIES:
            raise AnimeDLError('Incorrect quality: "{}"'.format(quality))

        self.url = url
        self.quality = quality
        self._callback = callback
        if self._callback:
            self._callback('Extracting episode info from page')
        self.getEpisodes()

    def getEpisodes(self):
        self._episodeIds = []
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')
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

    def __len__(self):
        return len(self._episodeIds)

    def __getitem__(self, index):
        ep_id = self._episodeIds[index]
        return Episode(ep_id, self.quality, callback=self._callback)


class Episode:
    _base_url = r'https://9anime.is/ajax/episode/info?id={0}&server=33'

    def __init__(self, episode_id, quality='720p', callback=None):

        if quality not in QUALITIES:
            raise AnimeDLError('Incorrect quality: "{}"'.format(quality))

        self.episode_id = episode_id
        self.quality = quality
        self._callback = callback
        if self._callback:
            self._callback("Extracting stream info of id: {}".format(self.episode_id))
        self.getData()

    def getData(self):
        url = self._base_url.format(self.episode_id)
        data = json.loads(requests.get(url).text)
        url = data.get('target')
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

    def download(self):
        print('[INFO] Downloading {}'.format(self.title))
        path = './' + self.title
        r = requests.get(self.stream_url, stream=True)

        total_size = r.headers['Content-length']
        downloaded, chunksize = 0, 2048
        start_time = time.time()

        if r.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=chunksize):
                    if chunk:
                        f.write(chunk)
                        downloaded += chunksize
                        write_status((downloaded), (total_size),
                                     start_time)


def write_status(downloaded, total_size, start_time):
    elapsed_time = time.time()-start_time
    rate = (downloaded/1024)/elapsed_time
    downloaded = float(downloaded)/1048576
    total_size = float(total_size)/1048576

    status = 'Downloaded: {0:.2f}MB/{1:.2f}MB, Rate: {2:.2f}KB/s'.format(
        downloaded, total_size, rate)

    sys.stdout.write("\r" + status + " "*5 + "\r")
    sys.stdout.flush()
