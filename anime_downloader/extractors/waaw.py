#!/usr/bin/env python3
# -*- coding:Utf-8 -*-
#waaw.py
import re
import json
import sys
from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
import logging

logger = logging.getLogger(__name__)

from anime_downloader import util
import os
import tempfile



chromedriver = util.check_in_path('chromedriver')
if not chromedriver:
    logger.warn(' "chromedriver" external web driver not supported')



class Waaw(BaseExtractor):
    def _get_data(self):
        url = self.url
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        
        logger.debug( f'_get_data url:{url} modulePath:{dir_path}' )
        
        template = "file://"+dir_path+'/waaw.html'
        #template = "file://"+dir_path+'/waaw_template.html'
        exploit = os.path.join(tempfile.gettempdir(), 'waaw_exploit.html')
        logger.debug( f'_get_data template:{template} exploit:{exploit}' )
        
        soup = helpers.soupify(helpers.get(template, sel=True))

        videoid = soup.select_one('#videoid').text
        videokeyorig = soup.select_one('#videokeyorig').text
        userid = soup.select_one('#userid').text
        cookieIndex = soup.select_one('#cookieIndex').text
        ddomain = soup.select_one('#ddomain').text
        
        shh = soup.select_one('#shh').text
        ashh = soup.select_one('#ashh').text
        tsh = soup.select_one('#tsh').text
       
        logger.debug( f'_get_data videoid:{videoid} videokeyorig:{videokeyorig} userid:{userid}' ) 
        logger.debug( f'_get_data cookieIndex:{cookieIndex} ddomain:{ddomain}' )
        logger.debug( f'_get_data shh:{shh} ashh:{ashh} tsh:{tsh}' )
          

        return {'stream_url': ''}


if __name__ == '__main__':
    util.setup_logger("DEBUG")
    logger = logging.getLogger("anime_downloader") 
    ext = Waaw('http://hqq.tv/watch_video.php?v=0CTzTlZClgIr', quality='480p', headers=None)
    ext._get_data()