from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers


class Wasabisys(BaseExtractor):
    def _get_data(self):

        return {
            'stream_url': self.url,
            'referer': 'https://animtime.com/'
        }
