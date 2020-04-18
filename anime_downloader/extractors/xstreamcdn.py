

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers

class XStreamCDN(BaseExtractor):
    def _get_data(self):
        post_data = helpers.post("https://www.xstreamcdn.com/api/source/" + self.url.split("/")[-1]).json()
        data = post_data["data"]
        link = data[-1]["file"]
        
        return {
                'stream_url': link,
        }
