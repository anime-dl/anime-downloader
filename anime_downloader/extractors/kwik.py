from base64 import b64decode
import requests
import logging
import re

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
from subprocess import CalledProcessError
from anime_downloader import util

logger = logging.getLogger(__name__)


class Kwik(BaseExtractor):
    YTSM = re.compile(r"ysmm = '([^']+)")

    KWIK_PARAMS_RE = re.compile(r'\("(\w+)",\d+,"(\w+)",(\d+),(\d+),\d+\)')
    KWIK_D_URL = re.compile(r'action="([^"]+)"')
    KWIK_D_TOKEN = re.compile(r'value="([^"]+)"')

    CHARACTER_MAP = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/"

    def get_string(self, content: str, s1: int, s2: int) -> str:
        slice_2 = self.CHARACTER_MAP[0:s2]

        acc = 0
        for n, i in enumerate(content[::-1]):
            acc += int(i if i.isdigit() else 0) * s1**n

        k = ''
        while acc > 0:
            k = slice_2[int(acc % s2)] + k
            acc = (acc - (acc % s2)) / s2

        return k or '0'

    def decrypt(self, full_string: str, key: str, v1: int, v2: int) -> str:
        v1, v2 = int(v1), int(v2)
        r, i = "", 0

        while i < len(full_string):
            s = ""
            while (full_string[i] != key[v2]):
                s += full_string[i]
                i += 1
            j = 0
            while j < len(key):
                s = s.replace(key[j], str(j))
                j += 1
            r += chr(int(self.get_string(s, v2, 10)) - v1)
            i += 1
        return r

    def decode_adfly(self, coded_key: str) -> str:
        r, j = '', ''
        for n, l in enumerate(coded_key):
            if not n % 2:
                r += l
            else:
                j = l + j

        encoded_uri = list(r + j)
        numbers = ((i, n) for i, n in enumerate(encoded_uri) if str.isdigit(n))
        for first, second in zip(numbers, numbers):
            xor = int(first[1]) ^ int(second[1])
            if xor < 10:
                encoded_uri[first[0]] = str(xor)

        return b64decode(("".join(encoded_uri)).encode("utf-8")
                         )[16:-16].decode('utf-8', errors='ignore')

    def bypass_adfly(self, adfly_url):
        session = requests.session()

        response_code = 302
        while response_code != 200:
            adfly_content = session.get(
                session.get(
                    adfly_url,
                    allow_redirects=False).headers.get('location'),
                allow_redirects=False)
            response_code = adfly_content.status_code
        return self.decode_adfly(self.YTSM.search(adfly_content.text).group(1))

    def get_stream_url_from_kwik(self, adfly_url):
        session = requests.session()

        f_content = requests.get(
            self.bypass_adfly(adfly_url),
            headers={
                'referer': 'https://kwik.cx/'
            }
        )
        decrypted = self.decrypt(
            *
            self.KWIK_PARAMS_RE.search(
                f_content.text
            ).group(
                1, 2,
                3, 4
            )
        )

        code = 419
        while code != 302:
            content = session.post(
                self.KWIK_D_URL.search(decrypted).group(1),
                allow_redirects=False,
                data={
                    '_token': self.KWIK_D_TOKEN.search(decrypted).group(1)},
                headers={
                    'referer': str(f_content.url),
                    'cookie': f_content.headers.get('set-cookie')})
            code = content.status_code

        return content.headers.get('location')

    def _get_data(self):
        return {
            'stream_url': self.get_stream_url_from_kwik(self.url),
            'referer': None
        }
