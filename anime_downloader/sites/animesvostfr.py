from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import logging
import re

from requests.exceptions import HTTPError
from anime_downloader import util
import click

logger = logging.getLogger(__name__)

youtube_dl_supported = True
try:   
    #from __future__ import unicode_literals
    import youtube_dl
    
    youtube_dl_supported = util.check_in_path('youtube-dl')
except ImportError:
    youtube_dl_supported = False
    # need: python3 -m pip install --upgrade youtube-dl
    logger.warn(' "youtube-dl" external downloader not supported')

class AnimesVOSTFR(Anime, sitename='animesvostfr'):
       
        sitename = 'animesvostfr'
        QUALITIES = ['360p', '480p', '720p', '1080p']
        DOMAIN = "https://www1.animesvostfr.net/"

        @classmethod
        def search(cls, query):
            
            soup = helpers.soupify(helpers.get(cls.DOMAIN, params={'s' : query}))
            
            results = []           
            for v in soup.select('div.movies-list > div.ml-item'):
                t = v.h2.text
                u = v.a['href']
                p = v.img['src']
                
                lang = v.select_one('div.language').text.upper()
                
                #logger.debug( "results: {}".format(lang) )
                
                eps = v.select_one('span.mli-quality').text.upper()               
                #logger.debug( "results: {}".format(eps) )
                
                #add part at the title like:
                #(VOSTR 12/12)
                #(VF 12/12)
                #(VF MOVIE)
                #...
                lang_dict = {
                'VOSTFR':f' (VOSTFR {eps})',
                'VF':f' (VF {eps})',
                'VO':f' (VO {eps})'
                }
                selected_lang = f' (V? {eps})' #default lang
                for a in lang_dict:
                    if a in lang.upper():
                        selected_lang = lang_dict[a]
                        break
                t += selected_lang
                
                #logger.debug( "title: %s", t )
 
                search_result_info = SearchResult(title=t, url=u, poster=p)
               
                results.append(search_result_info)
            logger.debug( "results: {}".format(results) )
            
            return results
        
        def _scrape_episodes(self):
            soup = helpers.soupify(helpers.get(self.url))

            episode_links = None
            results = [] 
            
            season = soup.find("div", id="seasonss")
            
            if season:
                episode_links = season.select('div.les-title > a')
                
            
            if episode_links:
            
                logger.debug( "episode_links: {}".format(episode_links) )
                
                #results = [a.get('href') for a in episode_links[::-1]]
                #results = [a.get('href') for a in episode_links]
                
                eps = []
                id = 0
                for ep in episode_links:
                    if ep.get('href') and ep.get('href') != '#':
                        logger.debug( '%s -> %s', ep.text.replace("• ", ""), ep.get('href') )
                        title = ep.text.strip()
                        id = id + 1
                        eps.append( SearchResult(title=title, url=ep.get('href'), meta={'id':str(id)} ) )
                
                click.echo(util.format_search_results(eps), err=True) 
            
                #Get Param episode_range
                episode_range_value = None
                ctx = click.get_current_context()
                episode_range = [x for x in ctx.command.params if x.name == "episode_range"][0]
                logger.debug("ctx.params: {}".format(ctx.params) )           
                if episode_range.expose_value:
                    episode_range_value = ctx.params[episode_range.name]
                logger.debug("episode_range: {}".format(episode_range_value) )
                
                if not episode_range_value:
                    episode_range_value = click.prompt('Enter the episode no (e.g. 1|1:5|1,2,5|1:5,7:8,12): ', type=str, default='1:'+str(len(eps)), err=True)
                
                eps_sel = util.parse_ep_str(eps, episode_range_value)
                results = [(ep.meta['id'], ep.url) for ep in eps_sel]
                
                logger.debug( "results: {}".format(results) )
            else:
                results.append(self.url)
                
            
            return results

        def _scrape_metadata(self):
            
            logger.debug("_scrape_metadata url: %s", str(self.url) )
            
            soup = helpers.soupify(helpers.get(self.url))
     
            h1 = soup.select_one('div.main-content h1')
            logger.debug("_scrape_metadata H1: %s", str(h1))
            
            title = h1.text.strip()
            while title.startswith( '.' ):
                title = title[1:].strip()
 
            self.title = title
            

class AnimesVOSTFREpisode(AnimeEpisode, sitename='animesvostfr'):
        
        link_stream_url = "https://www1.animesvostfr.net/ajax-get-link-stream/"
        
        SERVERS = [
            'rapidvideo', #gcloud
            'photoss', #gcloud embeded
            'opencdn', # ???
            'photos', #hydrax
            'photo'   #hydrax
        ]
        
        lastQualityQuery = None
        
        def FindBetterExtractor(self, url='', quality=None, ytdlMode=False):
            ext_servers_regex = {
                '^(?:http|https)://.*youtubedownloader\..+/v/.+$':['youtubedownloader','gcloud', url], # https://youtubedownloader.cx/v/1e660ijq873-ld
                '^(?:http|https)://.*gcloud\..+/v/.+$'           :['gcloud','gcloud', url],
                '^(?:http|https)://.*feurl\..+/v/.+$'            :['feurl','gcloud', url],
                '^(?:http|https)://.*fembed\..+/v/.+$'           :['fembed','gcloud', url], #https://www.fembed.net/v/ewy7-u-18pn8rzl
                '^(?:http|https)://.*hydrax\..+/.*v=.+$'         :['hydrax','hydrax', url]  #https://hydrax.net/watch?v=wZsRPKrmb
            }
            
            bestOK = False
            
            if ytdlMode: # Direct Link -> Aria2
                best_ext = ['youtube-dl','no_extractor', url]
            else:
                best_ext = ['unknown server','no_extractor', url]
            
            for k, v in ext_servers_regex.items():
                if re.match(k, url):
                    best_ext = v
                    bestOK = True
                    break
            
            if not ytdlMode and not bestOK and youtube_dl_supported: 
            
                info_dict = None
                ydl_opts = {'logger': logger}
                try:
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        ydl.cache.remove()
                        info_dict = ydl.extract_info(url, download=False)
                except Exception as ex:
                    logger.error("Not lucky: youtube-dl Failed (%s)", url )
                    #raise ex
                                   
                if info_dict:
                    #logger.debug("youtube-dl info_dict:{}".format(info_dict))
                     
                    urls = []
                    best_url = None    
                    if 'formats' in info_dict:
                        for format in info_dict['formats']:
                            protocol = format.get('protocol')
                            ext = format.get('ext')
                            url = format.get('url')
                            height = format.get('height')
                            format_note = format.get('format_note')
                            format_note2 = format.get('format')
                            
                            vcodec = format.get('vcodec')
                            if vcodec and 'none' in vcodec:
                                vcodec = None
                                
                            acodec = format.get('acodec')
                            if acodec and 'none' in acodec:
                                acodec = None
                            
                            format_quality = None
                            if not format_quality and height:
                                format_quality = str(height)+"p"
                            if not format_quality and format_note:
                                format_quality = format_note
                            if not format_quality and format_note2:
                                if 'sd' in format_note2:
                                    format_quality = '240p 480p'
                                elif 'hd' in format_note2:
                                    format_quality = '720p 1080p'
                            
                            logger.debug(f"youtube-dl format:{protocol}/{ext}/{vcodec}/{acodec}/{format_quality}/{format_note}/{format_note2}")
                            
                            if protocol in ['http', 'https'] and ext in ['mp4'] and ((vcodec and acodec) or not( vcodec or acodec )):                            
                                urls.append( {'quality':format_quality, 'url':url})
                                
                                
                                if not format_quality:
                                    logger.debug(f"youtube-dl format:{format}")
                                    
                                    
                                    
                                if not best_url and format_quality and quality in format_quality:
                                    best_url = url

                    logger.debug(f"youtube-dl urls:{urls}")
                    
                    if best_url:
                        #recursive
                        return self.FindBetterExtractor( best_url, quality, True )
                    
            return best_ext
        

        def _get_sources(self):
            
            # Swap multi Call to _get_sources when previous previous call return self._sources = [] = '' = None
            if self.lastQualityQuery == self.quality:
                return self._sources
            self.lastQualityQuery = self.quality
            
            #version = self.config['version'] 
            #server = self.config['server']
            #fallback = self.config['fallback_servers']
            config_servers = self.config['servers']
            logger.debug( "_get_sources dl_servers: {}".format(config_servers) )
                    
            logger.debug( "_get_sources url: %s", self.url )
            
            #https://www1.animesvostfr.net/ajax-get-link-stream/?server=rapidvideo&filmId=45532
            #-> https://there.to/v/-zln1apmp3g423r
            
            filmid = None
            episodeid = None
            episodenum = None
            
            soup = helpers.soupify(helpers.get(self.url, params={'server' : 'rapidvideo'}))
            
            shortlink = soup.find( 'link', {'rel': 'shortlink'})
            logger.debug( "shortlink: {}".format(shortlink) )
            if shortlink:
                #logger.debug( "shortlink2: {}".format(shortlink['href']) )
                ids = re.findall(r'.*/?p=([^"]+)', shortlink['href'])
                #logger.debug( "shortlink2: {}".format(ids) )
                if ids and len(ids) > 0:
                    filmid = ids[0]
                
                
            

            select = soup.select_one('div.list-episodes  select')
            option = None
            
            if select:
                option = select.find('option', {'selected': True})
            if option:
                episodeid = option['episodeid']
                episodenum = option.text
            
            logger.debug( "_get_sources  filmid: %s episodeid: %s episodenum: %s", str(filmid), str(episodeid), str(episodenum) )
            
            
            if not filmid:
                filmid = episodeid
                
            # Sample 1
            # 'rapidvideo': ''
            # 'photoss': 'https://play.comedyshow.to/embedplay/4a2faf54b99e8d1152e598b24916d0d9'
            # 'opencdn': 'https://lb.cartoonwire.to/public/dist/index.html?id=76eb47ca7bbf5a548938bf90a4bceaa8'
            # 'photos': 'https://hydrax.net/watch?v=wZsRPKrmb'
            # 'photo': 'https://hydrax.net/watch?v=wZsRPKrmb'
            #
            # Sample 2
            # 'rapidvideo': 'https://youtubedownloader.cx/v/1e660ijq873-ldr'
            # 'photoss': 'https://play.comedyshow.to/embedplay/d187decc7e7596c0c9ad831c4a09038d'
            # 'opencdn': 'https://lb.cartoonwire.to/public/dist/index.html?id=77790c2132de4b173c86db105a96b5af'
            # 'photos': 'https://hydrax.net/watch?v=pVkQjLHxO'
            # 'photo': 'https://hydrax.net/watch?v=pVkQjLHxO'
            #
            # Sample 3
            # 'rapidvideo': ''
            # 'photoss': 'https://play.comedyshow.to/embedplay/b6bab9c780325ff53644cbc4dba32558'
            # 'opencdn': 'https://lb.cartoonwire.to/public/dist/index.html?id=cb5c81f15593ae88cf17bebe0f73b177'
            # 'photos': 'https://hydrax.net/watch?v=rTaZnpvMdp'
            # 'photo': 'https://hydrax.net/watch?v=rTaZnpvMdp'
            #
            # Sample 4
            # 'rapidvideo': 'https://youtubedownloader.cx/v/xd33pu5401xy78p'
            # 'photoss': 'https://play.comedyshow.to/embedplay/1c047309aebdb11797aa93f0b689eb9f'
            # 'opencdn': 'https://lb.cartoonwire.to/public/dist/index.html?id=No m3u8Id'
            # 'photos': ''
            # 'photo': ''
            #
            #
            urls_server = {} 
            for serv in self.SERVERS:
                urls_server[serv] = helpers.get(self.link_stream_url, params={'server' : serv, 'filmId' : filmid}).text.strip()
               
            logger.debug( "_get_sources urls: {}".format(urls_server) )
            
            
            # Test Hydrax HD: anime -ll DEBUG dl "neverland" --provider animesvostfr -c 1 -e 1 -q 720p
            # Test Hydrax SD: anime -ll DEBUG dl "neverland" --provider animesvostfr -c 1 -e 1 -q 360p                            
            sources = []
            for serv in self.SERVERS:
                if urls_server[serv] and (urls_server[serv] > '') and (urls_server[serv].find('No m3u8Id') < 0):
                
                    logger.info( "%s", urls_server[serv] )
                    
                    soup = None
                    try:
                        soup = helpers.soupify(helpers.get(urls_server[serv]))
                    except HTTPError as err:
                        logger.debug("_get_sources HTTP Err: %s", str(err))
                    
                    if soup:
                        #logger.debug( "soup: {}".format(soup) )
                        
                        iframe = soup.select_one("iframe")
                        if iframe:
                            url = iframe['src'].strip()
                            if url and (url > ''):
                                logger.info( "%s -> %s", urls_server[serv], url )
                                urls_server[serv] = url 
                                
                                
                                
                    dl_serv, ext_serv, url_serv = self.FindBetterExtractor(urls_server[serv], self.quality)  
                    
                    logger.debug( "_get_sources server:%s extractor:%s", dl_serv, ext_serv )
                    
                    if ext_serv == 'no_extractor':
                        if not dl_serv in config_servers:
                            #if not in the list of sorted authorized servers
                            dl_serv = None
                     
                    if dl_serv:
                        sources.append({'extractor':ext_serv, 'server':dl_serv, 'url':url_serv, 'version':'subbed'})
                    else:
                        logger.warn( "_get_sources url: %s not supported", urls_server[serv])
                           
                       
            return self.sort_sources(sources)