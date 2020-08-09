from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers

class SendVid(BaseExtractor):
    def _get_data(self):
        soup = helpers.soupify(helpers.get(self.url))
        return soup.source['src']
