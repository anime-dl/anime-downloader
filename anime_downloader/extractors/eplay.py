
from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers

import base64
import re


class EPlay(BaseExtractor):
    def _get_data(self):
        text=helpers.get(self.url).text
        link=helpers.soupify(base64.b64decode(re.search('Base64.decode\("(.*)"\)', text).group(1)).decode()).iframe.get("src")
        direct_link=helpers.soupify(helpers.get(link)).source.get("src")

        return {
            'stream_url': direct_link,
            'referer': 'http://eplayvid.com/'
        }
