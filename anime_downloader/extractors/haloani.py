import logging
import re
import json
import base64

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)

class Haloani(BaseExtractor):
    def _get_data(self):
        url = self.url
        soup = helpers.soupify(helpers.get(url))
        src = 'https://haloani.ru/KickAssAnime/' + (soup.select('iframe')[0].get('src'))
        soup = helpers.get(src).text
        regex = r'Base64.decode\("[^"]*'
        decoded = base64.b64decode(re.search(regex,soup).group())
        regex = r'\[{[^\]]*\]'
        links = json.loads(re.search(regex,str(decoded)).group())
        link = links[0]['file'].replace('\\','')
        return {
            'stream_url': link,
            'referer': src,
        }