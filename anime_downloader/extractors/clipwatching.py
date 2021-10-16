from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
from anime_downloader.util import deobfuscate_packed_js
import re
import json

class clipwatching(BaseExtractor):
    def _get_data(self):
        fix_json = [['src:', '"src":'], ['type:', '"type":']]
        sources = re.search(r"sources:\s*(\[.*?\])", helpers.get(self.url).text).group(1)
        for x, y in fix_json:
            sources = sources.replace(x, y)
        sources = json.loads(sources)

        return {
            'stream_url': sources[0]['src'],
            'referer': self.url
        }