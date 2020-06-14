from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import logging
import re

from requests.exceptions import HTTPError

logger = logging.getLogger(__name__)

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
                results = [a.get('href') for a in episode_links]
                
                logger.debug( "results: {}".format(results) )
            else:
                results.append(self.url)
                
            
            return results

        def _scrape_metadata(self):
            
            logger.debug("_scrape_metadata url: %s", str(self.url) )
            
            soup = helpers.soupify(helpers.get(self.url))
     
            h1 = soup.select_one('div.main-content h1')
            logger.debug("_scrape_metadata H1: %s", str(h1))
            
            self.title = h1.text.strip()
            

class AnimesVOSTFREpisode(AnimeEpisode, sitename='animesvostfr'):
        
        link_stream_url = "https://www1.animesvostfr.net/ajax-get-link-stream/"
        
        SERVERS = [
            'rapidvideo', #gcloud
            'photoss', #gcloud embeded
            'opencdn', # ???
            'photos', #hydrax
            'photo'   #hydrax
        ]

        def _get_sources(self):
            
            #version = self.config['version'] 
            #server = self.config['server']
            #fallback = self.config['fallback_servers']
            dl_servers = self.config['servers']
            logger.debug( "_get_sources dl_servers: {}".format(dl_servers) )
            
            ext_servers = {
                'youtubedownloader':'gcloud',
                'gcloud':'gcloud',
                'feurl':'gcloud',
                'fembed':'gcloud',
                'hydrax':'hydrax'
            }            
            logger.debug( "_get_sources ext_servers: {}".format(ext_servers) )
            
            
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
                                logger.debug( "%s -> %s", urls_server[serv], url )
                                urls_server[serv] = url 
                     
                    notAppend = True       
                    for dl_serv in dl_servers:
                        ext = 'no_extractor'
                        if dl_serv in ext_servers:
                            ext = ext_servers[dl_serv]
                        
                        if dl_serv in urls_server[serv]:
                            sources.append({'extractor':ext, 'server':dl_serv, 'url':urls_server[serv], 'version':'subbed'})
                            notAppend = False
                            
                    if notAppend:
                        logger.warn( "_get_sources url: %s not supported", urls_server[serv])
               
                       
            return self.sort_sources(sources)
            
            
         