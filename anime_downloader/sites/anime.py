import requests
from bs4 import BeautifulSoup
import json
import re
import time
import sys
import os
import click


class AnimeDLError(Exception):
    pass


class URLError(AnimeDLError):
    pass


class NotFoundError(AnimeDLError):
    pass


class BaseAnime():
    def __init__(self, url, quality='720p', callback=None):

        if quality not in self.QUALITIES:
            raise AnimeDLError('Incorrect quality: "{}"'.format(quality))

        self.url = self.verify_url(url)

        if quality in self.QUALITIES:
            self.quality = quality
        else:
            raise AnimeDLError(f'Quality {quality} not found in {self.QUALITIES}')

        self._callback = callback
        if self._callback:
            self._callback('Extracting episode info from page')
        self.getEpisodes()

    def verify_url(self, url):
        return url

    def getEpisodes(self):
        self._episodeIds = []
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        return self._getEpisodeUrls(soup)

    def __len__(self):
        return len(self._episodeIds)

    def __getitem__(self, index):
        ep_id = self._episodeIds[index]
        return self._episodeClass(ep_id, self.quality, callback=self._callback)

    def _getEpisodeUrls(self, soup):
        return


class BaseEpisode:
    QUALITIES = None
    title = ''
    stream_url = ''

    def __init__(self, episode_id, quality='720p', callback=None):

        if quality not in self.QUALITIES:
            raise AnimeDLError('Incorrect quality: "{}"'.format(quality))

        self.episode_id = episode_id
        self.quality = quality
        self._callback = callback
        if self._callback:
            self._callback("Extracting stream info of id: {}".format(self.episode_id))
        self.getData()

    def getData(self):
        raise NotImplementedError

    def download(self, force=False):
        print('[INFO] Downloading {}'.format(self.title))
        path = './' + self.title
        r = requests.get(self.stream_url, stream=True)

        total_size = int(r.headers['Content-length'])
        downloaded, chunksize = 0, 16384
        start_time = time.time()

        if os.path.exists(path) and not force:
            if os.stat(path).st_size == total_size:
                print('[INFO] File already downloaded. Skipping download.')
                return

        if r.status_code == 200:
            with click.progressbar(length=int(total_size)) as bar:
                with open(path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=chunksize):
                        if chunk:
                            f.write(chunk)
                            downloaded += chunksize
                            # write_status((downloaded), (total_size),
                            #              start_time)
                            bar.update(chunksize)


def write_status(downloaded, total_size, start_time):
    elapsed_time = time.time()-start_time
    rate = (downloaded/1024)/elapsed_time
    downloaded = float(downloaded)/1048576
    total_size = float(total_size)/1048576

    status = 'Downloaded: {0:.2f}MB/{1:.2f}MB, Rate: {2:.2f}KB/s'.format(
        downloaded, total_size, rate)

    sys.stdout.write("\r\n" + status + " "*5 + "\r")
    sys.stdout.flush()
