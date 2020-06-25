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
        
        soup = helpers.soupify(helpers.get(url, sel=False))                       
        scripts = re.findall( r'<script>[^<>].*?</script>',
                              str(soup), re.MULTILINE | re.DOTALL )
        
        
        info_vars = None
        challenge_vars = None
        challenge = None               
        for script in scripts:
            m = re.search( r'var [^<>(){}]*videokeyorig.*?;',
                           str(script), re.MULTILINE | re.DOTALL )
            if m and not info_vars:
                info_vars = m.group(0)
            
            m = re.search( r'var [^<>(){}]*shh.*?;',
                           str(script), re.MULTILINE | re.DOTALL )
            if m and not challenge_vars:
                challenge_vars = m.group(0)
             
            # Seacrh if scprit contain chinese chars   
            m = re.findall(r'[\u4e00-\u9fff]+',
                           str(script), re.MULTILINE | re.DOTALL )
            if m and len(m) > 10 and not challenge:
                m = re.search( r"<script>(.*)</script>",
                               str(script), re.MULTILINE | re.DOTALL )
                if m and len(m.groups()) > 0:
                    challenge = m.group(1)
                
        
        #logger.debug( f'_get_data info_vars:{info_vars}\n\nchallenge_vars:{challenge_vars}\n\nchallenge:{challenge}' )
        if info_vars and challenge_vars and challenge:
        
            template = dir_path+'/waaw_template.html'
            exploit = os.path.join(tempfile.gettempdir(), 'waaw_exploit.html')
            exploiturl = "file://"+exploit
            logger.debug( f'_get_data template:{template} exploit:{exploit}' )
            
            soup = None
            with open(template, "rb") as file:
                soup = helpers.soupify(file.read())
            
            if soup:
                node = soup.select_one('#info_vars')
                if node:
                    node.string = info_vars
                    
                node = soup.select_one('#challenge_vars')
                if node:
                    node.string = challenge_vars
                     
                node = soup.select_one('#challenge')
                if node:
                    node.string = challenge
            
                html = soup.prettify("utf-8")
                #logger.debug( f'_get_data html:{html}' )
                with open(exploit, "wb") as file:
                    file.write(html)
                    
                soup = helpers.soupify(helpers.get(exploiturl, sel=True))
                if soup:
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
                
                #logger.debug( f'_get_data open {exploit}' )
                os.remove(exploit)
          

        return {'stream_url': ''}


if __name__ == '__main__':
    util.setup_logger("DEBUG")
    logger = logging.getLogger("anime_downloader") 
    #ext = Waaw('http://hqq.tv/watch_video.php?v=0CTzTlZClgIr', quality='480p', headers=None)
    ext = Waaw('http://hqq.watch/player/embed_player.php?vid=0CTzTlZClgIr&autoplay=no', quality='480p', headers=None)
    ext._get_data()