from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers


class EPlay(BaseExtractor):
    def _get_data(self):
        direct_link = helpers.soupify(helpers.get(self.url)).source.get("src")

        return {
            'stream_url': direct_link,
            'referer': 'http://eplayvid.com/'
        }
