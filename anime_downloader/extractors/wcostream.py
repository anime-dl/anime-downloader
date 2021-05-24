from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
import re


class WcoStream(BaseExtractor):
    def _get_data(self):
        try:
            if self.url.startswith('https://vidstream.pro/e'):
                base_url = 'https://vidstream.pro'
            elif self.url.startswith('https://mcloud.to/e/'):
                base_url = 'https://mcloud.to'
            else:
                return []

            html = helpers.get(self.url, referer='https://wcostream.cc/')
            id_ = re.findall(r"/e/(.*?)\?domain", self.url)[0]
            skey = re.findall(r"skey\s=\s['\"](.*?)['\"];", html.text)[0]

            apiLink = f"{base_url}/info/{id_}?domain=wcostream.cc&skey={skey}"
            referer = f"{base_url}/e/{id_}?domain=wcostream.cc"

            response = helpers.get(apiLink, referer=referer).json()

            if response['success'] is True:
                sources = [
                    {
                        'stream_url': x['file']
                    }
                    for x in response['media']['sources']
                ]
                return sources
            else:
                return []

        except Exception:
            return {"stream_url": ''}
