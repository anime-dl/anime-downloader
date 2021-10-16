import logging
import re

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
from requests.exceptions import HTTPError

logger = logging.getLogger(__name__)


class Yourupload(BaseExtractor):
    def _get_data(self):
        regex = r"file: '([^']*)"
        try:
            response = helpers.get(self.url)
        except HTTPError:
            logger.error('File not found.')
            return {'stream_url': ''}

        file = re.search(regex, response.text).group(1)
        return {
            'stream_url': file,
            'referer': self.url
        }
