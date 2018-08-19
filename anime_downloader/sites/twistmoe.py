from Crypto import Random
from Crypto.Cipher import AES
import base64
from hashlib import md5
import requests
from bs4 import BeautifulSoup
import warnings

from anime_downloader.sites.anime import BaseAnime, BaseEpisode, SearchResult


# Don't warn if not using fuzzywuzzy[speedup]
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from fuzzywuzzy import process

BLOCK_SIZE = 16
KEY = b"k8B$B@0L8D$tDYHGmRg98sQ7!%GOEGOX27T"


class TwistMoeEpisode(BaseEpisode):
    QUALITIES = ['360p', '480p', '720p', '1080p']

    def _get_sources(self):
        return [('no_extractor', self.url)]


class TwistMoe(BaseAnime):
    sitename = 'twist.moe'
    QUALITIES = ['360p', '480p', '720p', '1080p']
    _episodeClass = TwistMoeEpisode
    _api_url = "https://twist.moe/api/anime/{}/sources"

    @classmethod
    def search(self, query):
        r = requests.get('https://twist.moe')
        soup = BeautifulSoup(r.text, 'html.parser')
        all_anime = soup.select_one('nav.series').select('li')
        animes = []
        for anime in all_anime:
            animes.append(SearchResult(
                title=anime.find('span').contents[0].strip(),
                url='https://twist.moe' + anime.find('a')['href'],
                poster='',
            ))
        animes = [ani[0] for ani in process.extract(query, animes)]
        return animes

    def get_data(self):
        anime_name = self.url.split('/a/')[-1].split('/')[0]
        url = self._api_url.format(anime_name)
        episodes = requests.get(
            url,
            headers={
                'x-access-token': '1rj2vRtegS8Y60B3w3qNZm5T2Q0TN2NR'
            }
        )
        episodes = episodes.json()
        self.title = anime_name
        episode_urls = ['https://eu1.twist.moe' +
                        decrypt(episode['source'].encode('utf-8'), KEY).decode('utf-8')
                        for episode in episodes]

        self._episode_urls = [(i+1, episode_url) for i, episode_url in enumerate(episode_urls)]
        self._len = len(self._episode_urls)

        return self._episode_urls



# From stackoverflow https://stackoverflow.com/questions/36762098/how-to-decrypt-password-from-javascript-cryptojs-aes-encryptpassword-passphras
def pad(data):
    length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + (chr(length)*length).encode()


def unpad(data):
    return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]


def bytes_to_key(data, salt, output=48):
    # extended from https://gist.github.com/gsakkis/4546068
    assert len(salt) == 8, len(salt)
    data += salt
    key = md5(data).digest()
    final_key = key
    while len(final_key) < output:
        key = md5(key + data).digest()
        final_key += key
    return final_key[:output]


def decrypt(encrypted, passphrase):
    encrypted = base64.b64decode(encrypted)
    assert encrypted[0:8] == b"Salted__"
    salt = encrypted[8:16]
    key_iv = bytes_to_key(passphrase, salt, 32+16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    return unpad(aes.decrypt(encrypted[16:]))
