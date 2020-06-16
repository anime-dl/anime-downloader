import re
import json
import sys
from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
import logging

logger = logging.getLogger(__name__)

class Gcloud(BaseExtractor):
    def _get_data(self):
        url = self.url

        # TODO: Maybe put it in Option ?
        withPreserveServerPreference = True
        
        if not withPreserveServerPreference:  
            """gcloud uses the same video ID as other sites"""
            url = url.replace('fembed.com','gcloud.live')
            url = url.replace('feurl.com','gcloud.live')
            
            url = url.replace('gcloud.live/v/','gcloud.live/api/source/')
            if url.find('#') != -1:url = url[:url.find('#')] 
            url = (url[-url[::-1].find('/'):])
            data = helpers.post(f'https://gcloud.live/api/source/{url}').json()['data']
            
        else:      
            # Don't force on gcloud.live - to preserve server preference - see anime.AnimeEpisode.sort_sources()                 
            if url.find('#') != -1:url = url[:url.find('#')]
            urlapi = url.replace('/v/', '/api/source/' )
            data = helpers.post(urlapi, referer=url).json()['data']
            
    
        if data == 'Video not found or has been removed':
            logger.warning('File not found (Most likely deleted)')
            return {'stream_url': ''}
        
        for a in data:
            if a['label'] == self.quality:
                return {'stream_url': a['file']}
            

        return {'stream_url': ''}
