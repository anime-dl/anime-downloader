from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import base64
import json
import logging

logger = logging.getLogger(__name__)

class AniMixPlay(Anime, sitename='animixplay'):
    sitename='animixplay'
    @classmethod
    def search(cls, query):
        # V3 not supported
        v1 = helpers.soupify(helpers.post("https://animixplay.com/api/search/v1", 
            data = {"q2": query}, verify = False).json()['result']).select('p.name > a')
        v2 = helpers.soupify(helpers.post("https://animixplay.com/api/search/", 
            data = {"qfast2": query}, verify = False).json()['result']).select('p.name > a')
        #v3 = helpers.soupify(helpers.post("https://animixplay.com/api/search/v3", 
        #    data = {"q3": query}, verify = False).json()['result'])
        v4 = helpers.soupify(helpers.post("https://animixplay.com/api/search/v4", 
            data = {"q": query}, verify = False).json()['result']).select('p.name > a')
        # Meta will be name of the key in versions_dict
        versions_dict = {'v1':v1, 'v2':v2, 'v4':v4}
        logger.debug('Versions: {}'.format(versions_dict))
        data = []
        for i in versions_dict:
            for j in versions_dict[i]:
                data.append(SearchResult(
                    title = j.text,
                    url = 'https://animixplay.com' + j.get('href'),
                    meta = {'version': i}))

        return data


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
                # Has a list of mp4 links.
                return data
            elif '/v2/' in self.url:
                # Has elaborate list for all metadata on episodes.
                episodes = []
                for i in data:
                    info_dict = i.get('src',[{'file':''}])
                    # Looks like mp4 is always first in the list
                    episodes.append(info_dict[0].get('file',''))
                return episodes
        else:
            ep_list = soup.find('div', {'id':'epslistplace'}).get_text()
            logger.debug(ep_list)
            jdata = json.loads(ep_list)
            keyList = list(jdata.keys())
            del keyList[0]
            logger.debug(keyList)
            return [jdata[x] for x in keyList if '.' in jdata[x]]

    def _scrape_metadata(self):
        self.title = helpers.soupify(helpers.get(self.url).text).select_one("span.animetitle").get_text()

class AniMixPlayEpisode(AnimeEpisode, sitename='animixplay'):
    def _get_sources(self):
        logger.debug(self.url)
        if 'googleapis.com/' in self.url:
            return [('no_extractor', self.url)]
        else:
            return [('vidstream', self.url)]
