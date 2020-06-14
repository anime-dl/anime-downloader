import re
import json
import sys
from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
import logging

from requests.exceptions import HTTPError
from anime_downloader.config import Config

logger = logging.getLogger(__name__)

class Gcloud(BaseExtractor):
    def _get_data(self):
        url = self.url
        

        # TODO: Add fallback_qualities to BaseExtractor
        # Warning not perfect because use only fallback_qualities of DL (not watch)
        #fallback_qualities = self.fallback_qualities
        if True:
            fallback_qualities = Config['dl']['fallback_qualities']
        else:
            fallback_qualities = Config['watch']['fallback_qualities']
        logger.debug( "fallback_qualities: {}".format(fallback_qualities))


        # TODO: Maybe put it in Option ?
        withPreserveServerPreferenceAndFallbackQualities = True
        
        if withPreserveServerPreferenceAndFallbackQualities:
        
            # Don't force on gcloud.live - to preserve server preference - see anime.AnimeEpisode.sort_sources()
            # Use fallback_qualities
            #   e.g: quality': '360p' and 'fallback_qualities': ['480p', '720p', '1080p']
            # if 360p is not available, try to use 480p, ...
                    
            if url.find('#') != -1:url = url[:url.find('#')]
            urlapi = url.replace('/v/', '/api/source/' )
            
            data = None
            try:
                data = helpers.post(urlapi, referer=url).json()
            except HTTPError as err:
                logger.debug("_get_data HTTP Err: %s", str(err))
                
            if data:
                #logger.debug( "data: {}".format(data) )
                logger.debug( 'Success: %s', str(data['success']) )
                logger.debug( "data: {}".format(data['data']) )
                
                url_quality = {}
                
                for d in data['data']:
                    #logger.debug( "data: {}".format(d) )
                    
                    quality = d['label']
                    url = d['file']
                    
                    if not quality in url_quality:
                        url_quality[quality] = url                
                  
                logger.debug( "quality: {}".format(url_quality) )
                logger.debug( "quality by def: {}".format(self.quality) ) 
                logger.debug( "quality fallback: {}".format(fallback_qualities) )
                
                quality_chosen = None
                if self.quality in url_quality:
                    quality_chosen = url_quality[self.quality]
                else:
                    for quality in fallback_qualities:
                        if quality in url_quality:
                            quality_chosen = url_quality[quality_chosen]
                            
                if not quality_chosen:
                    quality_chosen = url_quality[0]   
                    
                logger.debug( "quality_chosen: %s", str(quality_chosen) )
                    
                if not quality_chosen:
                    logger.warning('File not found (Most likely deleted)')
                    return {'stream_url': ''}      
                
                return {'stream_url': quality_chosen}
                
        else:
            
            """gcloud uses the same video ID as other sites"""
            url = url.replace('fembed.com','gcloud.live')
            url = url.replace('feurl.com','gcloud.live')
            
            url = url.replace('gcloud.live/v/','gcloud.live/api/source/')
            if url.find('#') != -1:url = url[:url.find('#')] 
            url = (url[-url[::-1].find('/'):])
            data = helpers.post(f'https://gcloud.live/api/source/{url}').json()['data']
    
            if data == 'Video not found or has been removed':
                logger.warning('File not found (Most likely deleted)')
                return {'stream_url': ''}
            
            for a in data:
                if a['label'] == self.quality:
                    return {'stream_url': a['file']}
            

        return {'stream_url': ''}
