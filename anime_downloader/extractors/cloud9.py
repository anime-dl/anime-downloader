import re
import json
import sys
from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
import logging

logger = logging.getLogger(__name__)

class Cloud9(BaseExtractor):
    def _get_data(self):
        url = self.url.replace('https://cloud9.to/embed/','https://api.cloud9.to/stream/')
        data = helpers.get(url).json()['data']
        if data == 'Video not found or has been removed':
            logger.warning('File not found (Most likely deleted)')
            return {'stream_url': ''}
        
        return {'stream_url': data['sources'][0]['file']}
