
from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
import re

class SibNet(BaseExtractor):
    def _get_data(self):
        resp = helpers.get(self.url).text
        link = "https://video.sibnet.ru" + re.search('src:\s+?"(.*?mp4)"', resp).group(1)

        return {
            'stream_url': link,
            'referer': self.url
        }
