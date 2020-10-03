from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers


class StreamTape(BaseExtractor):
    def _get_data(self):
        return {
            'stream_url': 'https:' + helpers.soupify(helpers.get(self.url)).select("div#videolink")[0].text,
            'referer': self.url
        }
