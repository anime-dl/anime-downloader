import logging
import re
import json

from anime_downloader.config import Config
from anime_downloader.extractors.base_extractor import BaseExtractor
import anime_downloader.extractors as extractors
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)

class VidStream(BaseExtractor):
    def _get_data(self):
        
        '''
        Config:
        List of servers. Will use servers in order. 
        For example: ["hydrax","vidstream"] will prioritize the HydraX link.
        Available servers: links (below) and vidstream 
        '''

        links = {
        "gcloud":"https://gcloud.live/",
        "mp4upload":"https://www.mp4upload.com/",
        "cloud9":"https://cloud9.to",
        "hydrax":"https://hydrax.net"
        }

        url = self.url.replace('https:////','https://')
        url = url.replace('https://vidstreaming.io/download','https://vidstreaming.io/server.php')

        soup = helpers.soupify(helpers.get(url))

        servers = Config._read_config()['siteconfig']['vidstream']['servers']
        sources_regex = r'sources:(\[{.*?}])'
        sources = re.search(sources_regex,str(soup))

        linkserver = soup.select('li.linkserver')
        for a in servers:
            if a == 'vidstream':
                return self._get_link(sources)
            for b in linkserver:
                if b.get('data-video').startswith(links.get(a,'None')):
                    self.url = b.get('data-video')
                    return extractors.get_extractor(a)._get_data(self)
 
    def _get_link(self,sources):
        QUALITIES = {
            "360":[],
            "480":[],
            "720":[],
            "1080":[],
        }
        sources = sources.group(1)
        sources = sources.replace("'",'"') #json only accepts ""

        regex = r"[{|,][\n]*?[ ]*?[\t]*?[A-z]*?[^\"]:"
        for a in re.findall(regex,sources): #Because sometimes it's not valid json
            sources = sources.replace(a,f'{a[:1]}"{a[1:-1]}"{a[-1:]}') #replaces file: with "file":

        sources = json.loads(sources)

        for a in QUALITIES:
            for b in sources:
                if a in b.get('label',None):
                    QUALITIES[a].append(b.get('file',''),)

        stream_url = QUALITIES[self.quality[:-1]][0] if len(QUALITIES[self.quality[:-1]]) != 0 else ''

        if QUALITIES == {"360":[],"480":[],"720":[],"1080":[],}:
            stream_url = sources[0].get('file','') #In case nothing is found
            loggger.debug("The streaming link's quality cannot be identified.")

        return {
            'stream_url': stream_url,
            'referer': self.url
        }
