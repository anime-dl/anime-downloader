import re
import json
import sys
from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
import logging

logger = logging.getLogger(__name__)

class Gcloud(BaseExtractor):
    def _get_data(self):
        logger.debug('Gcloud url: {}'.format(self.url)) #Surprisingly not debug printed in anime.py
        """gcloud uses the same video ID as other sites"""
        id_regex = r'(gcloud\.live|fembed\.com|feurl\.com)/(v|api/source)/([^(?|#)]*)' #Group 3 for id
        gcloud_id = re.search(id_regex,self.url)
        if not gcloud_id:
            logger.error('Unable to get ID for url "{}"'.format(self.url)) 
            return {'stream_url': ''}

        gcloud_id = gcloud_id.group(3)
        data = helpers.post(f'https://gcloud.live/api/source/{gcloud_id}').json()['data']
        
        if data == 'Video not found or has been removed':
            logger.warning('File not found (Most likely deleted)')
            return {'stream_url': ''}
        
        for a in data:
            if a['label'] == self.quality:
                return {'stream_url': a['file']}

        return {'stream_url': ''}
