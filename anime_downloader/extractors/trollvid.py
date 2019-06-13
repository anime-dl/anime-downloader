import re

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers


class Trollvid(BaseExtractor):
    def _get_data(self):
        # TODO: Provide referer by source
        referer = 'https://anistream.xyz'

        req = helpers.get(self.url, referer=referer)
        stream_url = re.findall('<source src="(.*?)"', req.text)[0]

        return {
            'stream_url': stream_url
        }
