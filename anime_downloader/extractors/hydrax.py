from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
import logging
import base64

logger = logging.getLogger(__name__)


class Hydrax(BaseExtractor):
    def _get_data(self):
        url = self.url
        # Should probably be urlparse.
        end = url[url.find('=') + 1:]
        # Note that this url can change.
        obfuscated_url = helpers.post('https://ping.iamcdn.net/',
                                      data={'slug': end},
                                      referer=f'https://play.hydracdn.network/watch?v={end}',
                                      ).json()['url']

        decoded_url = base64.b64decode(obfuscated_url[-1] + obfuscated_url[:-1]).decode('utf-8')

        # HydraX uses www.url for high quality and url for low quality
        quality = '' if self.quality in ['360p', '480p'] else 'www.'

        return {
            'stream_url': f'https://{quality}{decoded_url}',
            'referer': url
        }
