import re
import json
from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
import logging

logger = logging.getLogger(__name__)

class Hydrax(BaseExtractor):
    def _get_data(self):
        url = self.url
        end = url[url.find('=')+1:]
        beg = json.loads(helpers.post('https://ping.idocdn.com/',
            data={'slug':end},
            referer=url,
            ).text)['url']

        link = f'https://{beg}'
        return {
            'stream_url': link,
            'referer': url
        }
