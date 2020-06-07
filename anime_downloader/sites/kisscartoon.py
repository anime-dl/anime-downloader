from anime_downloader.sites.kissanime import KissAnime
from anime_downloader.sites.anime import AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from anime_downloader.sites.exceptions import NotFoundError
import json
import logging
import re
import sys
logger = logging.getLogger(__name__)


class KisscartoonEpisode(AnimeEpisode, sitename='kisscartoon'):
    _base_url = ''
    VERIFY_HUMAN = False
    _episode_list_url = 'https://kisscartoon.is/ajax/anime/load_episodes_v2'
    QUALITIES = ['720p']

    def _get_sources(self):
        params = {
            's': 'oserver',
            'episode_id': self.url.split('id=')[-1],
        }
        servers = ['xserver','ptserver','oserver','hserver']
        body_regex = r'<body>([^<]*?)<\/body>'
        api = helpers.post(self._episode_list_url,
                          params=params,
                          referer=self.url).json()
        
        iframe_regex = r'<iframe src="([^"]*?)"'
        url = re.search(iframe_regex,api['value']).group(1)
        #there should probably be an extractor here instead
        res = helpers.get(url, referer=self.url).text
        file_regex = r'"file":"(http[^"]*?)"'
        file = re.search(file_regex,res).group(1).replace('\\','')
        return [('no_extractor',file)]


class KissCartoon(KissAnime, sitename='kisscartoon'):
    sitename='kisscartoon'

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.get(
            'https://kisscartoon.is/Search/',
            params=dict(s=query),
            sel=True,
        ))

        ret = []
        for res in soup.select('.listing a'):
            res = SearchResult(
                title=res.text.strip('Watch '),
                url=res.get('href'),
                poster='',
            )
            logger.debug(res)
            ret.append(res)

        return ret

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url, sel=True))
        ret = [str(a['href'])
               for a in soup.select('.listing a')]

        if ret == []:
            err = 'No episodes found in url "{}"'.format(self.url)
            args = [self.url]
            raise NotFoundError(err, *args)

        return list(reversed(ret))
