from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
import logging
import base64

logger = logging.getLogger(__name__)

class Hydrax(BaseExtractor):
    def _get_data(self):
        url = self.url
        end = url[url.find('=')+1:]
        obfuscated_url = helpers.post('https://ping.idocdn.com/',
            data={'slug':end},
            referer=url,
            ).json()['url']

        decoded_url = base64.b64decode(obfuscated_url[-1] + obfuscated_url[:-1]).decode('utf-8')

        # HydraX uses www.url for high quality and url for low quality
        quality = '' if self.quality in ['360p','480p'] else 'www.'

        return {
            'stream_url': f'https://{quality}{decoded_url}',
            'referer': url
        }
