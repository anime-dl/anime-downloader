from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import base64
import json
import re
import logging

logger = logging.getLogger(__name__)

class AniMixPlay(Anime, sitename='animixplay'):
    sitename='animixplay'
    @classmethod
    def search(cls, query):
        jsonVar = helpers.post("https://animixplay.com/api/search/", data = {"qfast": query}, verify = False).json()
        logger.debug(jsonVar)
        soup = helpers.soupify(jsonVar["result"]).select('div.details a:not([href*=v3]):not([href*=v2])')#        logger.debug(soup)
        search_results = [
            SearchResult(
                title = a.text,
                url = 'https://animixplay.com' + a.get('href')
            )
            for a in soup
        ]
        return(search_results)

    def _scrape_episodes(self):
        url = self.url
        soup = helpers.soupify(helpers.get(url))
        # v1 and v3 is embedded video player
        # v2 and v4 is json post request
        if '/v2/' in self.url or '/v4/' in self.url:
            # Uses the id in the url and encodes it twice
            # NaN and N4CP9Eb6laO9N are permanent encoded variables found in
            # https://animixplay.com/assets/v4.min.js
            url_id = str.encode(self.url.split("/")[4])
            post_id = f'NaN{base64.b64encode(url_id).decode()}N4CP9Eb6laO9N'.encode()
            post_id = base64.b64encode(post_id).decode()
            data_id = 'id2' if '/v4/' in self.url else 'id'
            data = (helpers.post('https://animixplay.com/raw/2ENCwGVubdvzrQ2eu4hBH',
                data={data_id:post_id}).json())
            logger.debug(data)
            if '/v4/' in self.url:
                return [x for x in data]
            elif '/v2/' in self.url:
                for x in data: 
                    logger.debug("")
                    raise NotImplementedError
            else:
                logger.error("What have you done? you managed to bypass the first check. good job and have a pat on the back. BTW this wasnt supposed to happen")
        else:
            ep_list = soup.find('div', {'id':'epslistplace'}).get_text()
            logger.debug(ep_list)
            jdata = json.loads(ep_list)
            keyList = list(jdata.keys())
            del keyList[0]
            logger.debug(keyList)
            return [jdata[x] for x in keyList]

    def _scrape_metadata(self):
        self.title = helpers.soupify(helpers.get(self.url).text).select_one("span.animetitle").get_text()

class AniMixPlayEpisode(AnimeEpisode, sitename='animixplay'):
    def _get_sources(self):
        logger.debug(self.url)
        if 'googleapis.com/' in self.url:
            return [('no_extractor', self.url)]
        else:
            return [('vidstream', self.url)]
