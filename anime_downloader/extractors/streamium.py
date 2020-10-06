from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class Streamium(BaseExtractor):
    def _get_data(self):
        fragment = urlparse(self.url).fragment
        logger.debug('Fragment: {}'.format(fragment))
        url = 'https://streamium.xyz/gocdn.php?v=' + fragment
        file = helpers.get(url, referer=self.url).json()
        if file.get('file'):
            return {
                'stream_url': file.get('file'),
                'referer': url
            }

        logger.debug(file)
        return {'stream_url': ''}
