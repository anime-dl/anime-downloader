import re

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers

class Vudeo(BaseExtractor):
    def _get_data(self):
        soup = str(helpers.get(self.url).text)
        # Group 3 is the url
        source_regex = r"source(s|):\s*\[(\"|')(.[^\"|']*)"
        source = re.search(source_regex, soup)
        if source:
            url = source.group(3)
            return {
                'stream_url': url,
                'referer': self.url
            }
        else:
            return {'stream_url': ''}
