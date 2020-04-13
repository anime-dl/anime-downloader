import logging
import re
from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)

class VidStream(BaseExtractor):
    def _get_data(self):
        QUALITIES = {
        "360":[],
        "480":[],
        "720":[],
        "1080":[],
        }

        url = self.url.replace('https:////','https://')
        soup = helpers.get(url).text
        regex = r'https://vidstreaming\.io/download\?[^"]*'
        download = re.search(regex,soup).group()
            
        soup = helpers.soupify(helpers.get(download))
        links = soup.select('div.mirror_link')[0].select('div.dowload > a')
        
        for a in QUALITIES:
            for b in links:
                if a in b.text:
                    QUALITIES[a].append(b.get('href'))

        stream_url = QUALITIES[self.quality[:-1]][0] if QUALITIES != {"360":[],"480":[],"720":[],"1080":[],} else links[0].get('href') #In case nothing is found
        return {
            'stream_url': stream_url,
            'referer': download
        }
