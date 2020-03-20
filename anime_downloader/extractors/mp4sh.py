import logging
import re

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)

class MP4Sh(BaseExtractor):
    def _get_data(self):
        referer = 'https://ww5.dubbedanime.net/'
        soup = helpers.get(self.url, referer=referer).text
        url = re.search(r'source src="[^"]*',soup).group().replace('source src="','')
        return {'stream_url': url}