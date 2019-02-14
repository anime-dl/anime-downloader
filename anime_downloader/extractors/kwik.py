import logging
import re
from bs4 import BeautifulSoup
import requests
from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader import session

session = session.get_session()


class Kwik(BaseExtractor):
    '''Extracts video url from kwik pages, Kwik has some `security` 
       which allows to access kwik pages when only refered by something
       and the kwik video stream when refered through the corresponding 
       kwik video page.
    '''
    def _get_data(self):
        
        #Need a javascript deobsufication api/python, so someone smarter
        #than me can work on that for now I will add the pattern I observed

        #alternatively you can pattern match on `src` for stream_url part 
        source_parts_re = re.compile(r'action=\"([^"]+)\".*value=\"([^"]+)\".*Click Here to Download',
                                       re.DOTALL)

        #Kwik servers don't have direct link access you need to be referred
        #from somewhere, I will just use the url itself.
        
        download_url = self.url.replace('kwik.cx/e/', 'kwik.cx/f/')   

        kwik_text = session.get(download_url, headers={'referer': download_url }).text
        post_url,token = source_parts_re.search(kwik_text).group(1,2)
        
        stream_url = session.post(post_url,
                                headers = {'referer': download_url},
                                data = {'_token': token},
                                allow_redirects = False).headers['Location']
        
        title = stream_url.rsplit('/',1)[-1].rsplit('.',1)[0]
        
        logging.debug('Stream URL: %s' % stream_url)
        return {
            'stream_url': stream_url,
            'meta': {
                'title': title,
                'thumbnail': ''
            },
            'referer': None
        }
