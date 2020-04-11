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
