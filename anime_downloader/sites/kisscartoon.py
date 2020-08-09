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
    _episode_list_url = 'https://kisscartoon.is/ajax/anime/load_episodes_v2'
    QUALITIES = ['720p']

    def _get_sources(self):
        servers = self.config['servers']
        url = ''
        for i in servers:
            params = {
                's': i,
                'episode_id': self.url.split('id=')[-1],
            }
            api = helpers.post(self._episode_list_url,
                              params=params,
                              referer=self.url).json()
            if api.get('status',False):
                iframe_regex = r'<iframe src="([^"]*?)"'
                url = re.search(iframe_regex,api['value']).group(1)
                if url.startswith('//'):
                    url = 'https:' + url
                if url.endswith('mp4upload.com/embed-.html') or url.endswith('yourupload.com/embed/'): #Sometimes returns empty link
                    url = ''
                    continue
                break

        extractor = 'streamx' #defaut extractor
        extractor_urls = { #dumb, but easily expandable, maps urls to extractors
        "mp4upload.com":"mp4upload",
        "yourupload.com":"yourupload"
        }
        for i in extractor_urls:
            if i in url:
                extractor = extractor_urls[i]

        return [(extractor,url)]


class KissCartoon(KissAnime, sitename='kisscartoon'):
    sitename='kisscartoon'

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.get(
            'https://kisscartoon.is/Search/',
            params=dict(s=query),
            sel=True,
        ).text)

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
        soup = helpers.soupify(helpers.get(self.url, sel=True).text)
        ret = [str(a['href'])
               for a in soup.select('.listing a')]

        if ret == []:
            err = 'No episodes found in url "{}"'.format(self.url)
            args = [self.url]
            raise NotFoundError(err, *args)

        return list(reversed(ret))


    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url, sel=True).text)
        self.title = soup.select("a.bigChar")[0].text
