from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
import re
import logging

logger = logging.getLogger(__name__)

class StreamX(BaseExtractor):
    def _get_data(self):
        url = self.url
        referer = 'https://kisscartoon.nz/'
        res = helpers.get(url, referer=referer).text
        file_regex = r'"file":"(http[^"]*?)"'
        file = re.search(file_regex,res)
        if file:
            file = file.group(1).replace('\\','')
        else:
            logger.warning('File not found (Most likely deleted)')
            return {'stream_url': ''}

        return {
        'stream_url': file,
        'referer': self.url
        }
