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
        
        """gcloud uses the same video ID as other sites"""
        url = url.replace('fembed.com','gcloud.live')
        url = url.replace('feurl.com','gcloud.live')
        
        url = url.replace('gcloud.live/v/','gcloud.live/api/source/')

        if url.find('#') != -1: #cuts off the # at the end, used for subtitles
            url = url[:url.find('#')]

        #Returns the last non-empty string from url (separated with /), which is the id
        source_id = list(filter(lambda x: x, url.split('/')[::-1]))[0]
        data = helpers.post(f'https://gcloud.live/api/source/{source_id}').json()['data']
        
        if data == 'Video not found or has been removed':
            logger.warning('File not found (Most likely deleted)')
            return {'stream_url': ''}
        
        for a in data:
            if a['label'] == self.quality:
                return {'stream_url': a['file']}

        return {'stream_url': ''}
