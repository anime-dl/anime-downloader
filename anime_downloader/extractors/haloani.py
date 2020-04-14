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
        for a in range(10):
            soup = helpers.soupify(helpers.get(url))
            regex = r"(PHNjcmlwd[^\"]{90,})|Base64\.decode\(\"([^\"]{90,})"
            decode = re.search(regex,str(soup))
            if decode:
                decoded = base64.b64decode(decode.groups()[-1]+'==')
                break

            regex = r"window\.location = '(https://haloani\.ru/[^']*)"
            window = re.search(regex,str(soup))
            
            if window:
                url = window.group(1)
                continue
            if len(soup.select('iframe')) == 0:
                decoded = str(soup)
                break
            else:
                url = url[:url[19:].find('/')+20] #gets the base url
                url = url + soup.select('iframe')[0].get('src')

        if 'file' not in str(decoded) and 'src=' not in str(decoded):
            return {'stream_url': '',}
        if decoded[:6] == b'<video':
            regex = r"src=\"([^\"]*)"
            link = re.search(regex,str(decoded)).group(1)

        else:
            regex = r'\[{[^\]]*\]'
            links = re.search(regex,str(decoded)).group()
            regex = r"[{|,][\n]*?[ ]*?[\t]*?[A-z]*?[^\"]:"
            for a in re.findall(regex,links): #Because sometimes it's not valid json
                links = links.replace(a,f'{a[:1]}"{a[1:-1]}"{a[-1:]}') #replaces file: with "file": 

            links = json.loads(links)
            link = links[0]['file'].replace('\\','')
        return {
            'stream_url': link,
        }