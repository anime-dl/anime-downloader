from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import logging
import re

logger = logging.getLogger(__name__)

class AnimesVOSTFR(Anime, sitename='animesvostfr'):
       
        sitename = 'animesvostfr'
        QUALITIES = ['360p', '480p', '720p', '1080p']
        DOMAIN = "https://www1.animesvostfr.net/"

        @classmethod
        def search(cls, query):
            
            soup = helpers.soupify(helpers.get(cls.DOMAIN, params={'s' : query}, cf=True))
            
            results = []
            
            for v in soup.select('div.movies-list > div.ml-item'):
                t = v.h2.text
                u = v.a['href']
                p = v.img['src']
                
                lang = v.select_one('div.language').text.upper()
                
                #logger.debug( "results: {}".format(lang) )
                
                eps = v.select_one('span.mli-quality').text.upper()
                
                #logger.debug( "results: {}".format(eps) )
                
                if re.search('VOSTFR', lang, re.IGNORECASE):
                    t += ' (VOSTFR '+eps+')'
                elif re.search('VF', lang, re.IGNORECASE):
                    t += ' (VF '+eps+')'
                elif re.search('VO', lang, re.IGNORECASE):
                    t += ' (VO '+eps+')'
                else:
                    t += ' (V? '+eps+')'
                    
                
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
            
            soup = helpers.soupify(helpers.get(self.url, cf=True))
     
            h1 = soup.select_one('div.main-content h1')
            logger.debug("_scrape_metadata H1: %s", str(h1))
            
            self.title = h1.text.strip()
            

class AnimesVOSTFREpisode(AnimeEpisode, sitename='animesvostfr'):
        episodeId_url = 'https://www1.animesvostfr.net/api/episode'
        stream_url = 'https://www1.animesvostfr.net/api/videos?episode_id'
        anime_url = 'https://www.www1.animesvostfr.net/shows'
        
        link_stream_url = "https://www1.animesvostfr.net/ajax-get-link-stream/"
        
        SERVERS = [
            'rapidvideo',
            'photoss'
        ]

        def _get_sources(self):
            
            #version = self.config['version'] 
            #server = self.config['server']
            #fallback = self.config['fallback_servers']
            
            logger.debug( "_get_sources url: %s", self.url )
            
            #https://www1.animesvostfr.net/ajax-get-link-stream/?server=rapidvideo&filmId=45532
            #-> https://there.to/v/-zln1apmp3g423r
            
            filmid = None
            episodeid = None
            episodenum = None
            
            soup = helpers.soupify(helpers.get(self.url, params={'server' : 'rapidvideo'}, cf=True))
            
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
            
            episodeurl = None
            if filmid:
                episodeurl = helpers.get(self.link_stream_url, params={'server' : 'rapidvideo', 'filmId' : filmid}, cf=True).text.strip()
                
                if not episodeurl or episodeurl == '':
                    episodeurl = helpers.get(self.link_stream_url, params={'server' : 'photoss', 'filmId' : filmid}, cf=True).text.strip()
                    
            else:
                raise NotFoundError
                
            logger.debug( "_get_sources url:%s", episodeurl )
            
            
            
            
            #https://youtubedownloader.cx/v/y0661ue6-8jzj34
            #https://youtubedownloader.cx/api/source/y0661ue6-8jzj34
            
            
            #https://play.comedyshow.to/embedplay/4a2faf54b99e8d1152e598b24916d0d9
            #<iframe src="https://www.fembed.net/v/1ekm5ij-3l2rp8p"
            #https://feurl.com/api/source/1ekm5ij-3l2rp8p
            # POST r: https://play.comedyshow.to
            #d: feurl.com
            
            episodeurl1 = episodeurl          
            episodeurlapi1 = episodeurl1.replace('/v/', '/api/source/' )
            
            episodeurl2 = ''
            episodeurlapi2 = ''
            
            soup = helpers.soupify(helpers.get(episodeurl, cf=True))
            #logger.debug( "results: {}".format(soup) )
            
            iframe = soup.select_one("iframe")
            if iframe:
                episodeurl2 = iframe['src']
                
                logger.debug( "_get_sources episodeurl2:%s", episodeurl2 )
                
                episodeurlapi2 = episodeurl2.replace('/v/', '/api/source/' )
                
            
            logger.debug( "_get_sources episodeurlapi1:%s", episodeurlapi1 )    
            logger.debug( "_get_sources episodeurlapi2:%s", episodeurlapi2 )   
            
            #data = helpers.post(episodeurlapi, params={'r' : '', 'd' : 'youtubedownloader.cx' }, referer=episodeurl, cf=True).json()
            #data = helpers.post(episodeurlapi, params={'r' : '', 'd' : '' }, referer=episodeurl).json()
            #data = helpers.post(episodeurlapi, params={'r' : '' }, referer=episodeurl).json()
            
            data = None
            if episodeurlapi2:
                data = helpers.post(episodeurlapi2, referer=episodeurl2).json()
            elif episodeurlapi1:
                data = helpers.post(episodeurlapi1, referer=episodeurl1).json()
                
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
                        #self.__emails.append(email)
                        url_quality[quality] = url
                 
                  
                logger.debug( "quality: {}".format(url_quality) )
                logger.debug( "quality by def: {}".format(self.quality) ) 
                logger.debug( "quality fallback: {}".format(self._parent._fallback_qualities) )
                
                quality_chosen = None
                if self.quality in url_quality:
                    quality_chosen = url_quality[self.quality]
                else:
                    for quality in self._parent._fallback_qualities:
                        if quality in url_quality:
                            quality_chosen = url_quality[quality_chosen]
                            
                if not quality_chosen:
                    quality_chosen = url_quality[0]   
                    
                logger.debug( "quality_chosen: %s", str(quality_chosen) );
                    
                if not quality_chosen:
                    raise NotFoundError      
                
                return [('no_extractor', quality_chosen)]
            
            raise NotFoundError

            
            
         