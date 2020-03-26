import logging
import re
import sys
from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)

class VidStream(BaseExtractor):
    def _get_data(self):
        url = self.url.replace('https:////','https://')
        soup = helpers.get(url).text
        regex = r'https://vidstreaming\.io/download\?[^"]*'
        download = re.search(regex,soup).group()
            
        soup = helpers.soupify(helpers.get(download))
        link = soup.select('div.dowload > a')[0].get('href')
        
        return {
            'stream_url': link,
            'referer': download
        }