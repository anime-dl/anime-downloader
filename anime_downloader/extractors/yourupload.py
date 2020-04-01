import logging
import re

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)

class Yourupload(BaseExtractor):
    def _get_data(self):
        regex = r"file: '([^']*)"
        file = re.search(regex,helpers.get(self.url).text).group(1)
        return {
            'stream_url': file,
            'referer': self.url
        }