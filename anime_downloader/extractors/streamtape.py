from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers

import re


class StreamTape(BaseExtractor):
    def _get_data(self):
        resp = helpers.get(self.url, cache=False).text
        groups = re.search(
            r"document\.getElementById\(.*?\)\.innerHTML = [\"'](.*?)[\"'] \+ [\"'](.*?)[\"']",
            resp
        )
        url = "https:" + groups[1] + groups[2]
            

        return {
            'stream_url': url,
            'referer': self.url
        }
