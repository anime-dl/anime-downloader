import logging
import re
from bs4 import BeautifulSoup

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader import session

session = session.get_session()


class Kwik(BaseExtractor):
    '''Extracts video url from mp4upload embed pages, performs a request
    back to the non-embed mp4upload page to extract the title of the video
    albeit imperfectly as mp4upload doesn't place full title on the main
    page of whichever video you are dealing with.
    '''
    def _get_data(self):
        
        #Need a javascript deobsufication api/python, so someone smarter
        #than me can work on that for now I will add the pattern I observed

        #alternatively you can pattern match on `src` for stream_url part 
        source_parts_re = re.compile(r'\[{".":"([^"]+).*\'(.*)\'\.split\(\'\|\'\)',
                                        re.DOTALL)
        
        #Kwik servers don't have direct link access you need to be referred
        #from somewhere, I will just use the url itself.
        mp4u_embed = session.get(self.url, headers={'referer': self.url}).text
        
        stream_url_pattern, source_parts_list = source_parts_re.search(mp4u_embed).group(1,2)
        source_parts_list = source_parts_list.split('|')
        stream_url = ""
        print('fkme')
        for i in stream_url_pattern:
            ii = ord(i)
            if ( 48 <= ii <= 57):
                list_index = ii - 48 
            elif (97 <= ii <= 122):
                list_index = ii - 87
            elif (65 <= ii <= 90):
                list_index = ii - 29
            else:
                stream_url += i
                continue
            buf = source_parts_list[list_index]
            stream_url += buf if buf else i
        
        title = stream_url.rsplit('/',1)[-1].rsplit('.',1)[0]
        
        logging.debug('Stream URL: %s' % stream_url)

        return {
            'stream_url': stream_url,
            'meta': {
                'title': title,
                'thumbnail': ''
            },
            'referer': self.url
        }
