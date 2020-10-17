from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers

import re


class StreamTape(BaseExtractor):
    def _get_data(self):
        resp = helpers.get(self.url, cache=False).text
        url = "https:" + \
            re.search(
                "document\.getElementById\([\"']videolink[\"']\)\.innerHTML.*?=.*?[\"'](.*?)[\"']", resp).group(1)

        return {
            'stream_url': url,
            'referer': self.url
        }
