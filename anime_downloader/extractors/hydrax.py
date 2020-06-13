import re
import json
from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
import logging

logger = logging.getLogger(__name__)

class Hydrax(BaseExtractor):
    def _get_data(self):
        url = self.url
        
        extVer = None
        if not hasattr(self, 'extractorVersion'):
            setattr(self, 'extractorVersion', 1)            
        extVer = getattr(self, 'extractorVersion')
        logger.debug( "extVer: {}".format(extVer))
        
        fallback_qualities = None
        if not hasattr(self, 'fallback_qualities'):
            setattr(self, 'fallback_qualities', None)            
        fallback_qualities = getattr(self, 'fallback_qualities')
        logger.debug( "fallback_qualities: {}".format(fallback_qualities))


        # Reinit to V1 for next Call by an another site config
        #setattr(self, 'extractorVersion', 1)
        
        if extVer == 1:
            end = url[url.find('=')+1:]
            beg = json.loads(helpers.post('https://ping.idocdn.com/',
                data={'slug':end},
                referer=url,
                ).text)['url']
                
    
            logger.debug( "Hydrax _get_data: {}".format(beg) )
    
            link = f'https://{beg}'
            return {
                'stream_url': link,
                'referer': url
            }
            
        else:
            #TODO Finish it for : anime -ll DEBUG dl "neverland" --provider animesvostfr -c 1 -e 1
            
            
            return {'stream_url': ''}
