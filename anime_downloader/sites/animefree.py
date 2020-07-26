import logging
import re
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

class AnimeFree(Anime, sitename='animefree'): 
        sitename = 'kissanimefree'
        url = f'https://{sitename}.xyz/'
        @classmethod
        def search(cls, query):
            search_results = helpers.soupify(helpers.get(cls.url, params={'s': query})).select('div.movie-poster')   

            # i.select("a")[0].get('href').replace("kissanime","_anime") +"," + i.select("span")[0].get('data-id') ) 
            # ^ this will pass all data required directly to _scrape_episodes if you want to get rid of one or two get requests

            # The feature of passing links directly to anime-downloader makes passing data between functions convoluted
            # and creates a bunch un unnecessary get requests, because of this you gotta do at least 2 extra get requests
            # this also creates bugs when sitenames are similar
            search_results = [
                SearchResult(
                    title=i.select("a > img")[0].get("alt"),
                    url= i.select("a")[0].get('href').replace("kissanime","_anime"))
                for i in search_results
            ] 
            return search_results


        def _scrape_episodes(self): 
            #This is retarded, you need to replace the url, otherwise it will go to the kissanime site because the links are similar
            _referer = self.url.replace("_anime", "kissanime")
            _id = helpers.soupify( helpers.get(_referer)).select("li.addto-later")[0].get("data-id")

            #data = self.url.split(",")
            #_id = data[1]
            #_referer = data[0].replace("_anime", "kissanime")
            for i in range(1,100):
                d = helpers.get("https://kissanimefree.xyz/load-list-episode/", params = {"pstart":i, "id":_id, "ide":""}) 
                if not d.text: # MOVIES
                    maxEp = 1
                    break
                maxEp = int(helpers.soupify(d).select("li")[0].text)
                if not maxEp == i*100: 
                    break 
            return [f"{i},{_id},{_referer}" for i in range(1,maxEp+1)] 
            # you gotta know all three, the id of the episode, the id of the movie, and the referer


        def _scrape_metadata(self):
            realUrl = self.url.replace("_anime", "kissanime") 
            soup = helpers.soupify(helpers.get(realUrl)).select('div.film > h1')
            self.title = soup[0].text


class AnimeFreeEpisode(AnimeEpisode, sitename='kissanimefree'):
        def _get_sources(self):
            ids = self.url.split(",")
            ep = ids[0]
            realId = int(ids[0]) + int(ids[1]) + 2
            _referer = ids[2]

            realUrl = helpers.post("https://kissanimefree.xyz/wp-admin/admin-ajax.php",
                referer=f"https://kissanimefree.xyz/episode/{_referer}-episode-{realId}/",
                data={"action":"kiss_player_ajax","server":"vidcdn","filmId":realId}).text

            realUrl = realUrl if realUrl.startswith('http') else "https:" + realUrl

            txt = helpers.get(realUrl).text
            # Group 2 and/or 3 is the vidstreaming links without https://
            # Not used because I've yet to test if goto always leads to mp4
            # vidstream_regex = r"window\.location\s=\s(\"|').*?(vidstreaming\.io/[^(\"|')]*?)\"|(vidstreaming\.io/goto\.php[^(\"|')]*?)(\"|')"

            vidstream_regex = r"window\.location\s=\s(\"|').*?(vidstreaming\.io/[^(\"|')]*?)\""
            surl = re.search(vidstream_regex,txt)
            if surl:
                if surl.group(2):
                    return [('vidstreaming', surl.group(2),)]
            return ''
