import re
from urllib.parse import urlparse
from datetime import datetime
from requests import Request

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from anime_downloader.const import get_random_header

_headers = get_random_header() | { 'X-Requested-By': 'animestar-web'}


class AnimeStar(Anime, sitename='animestar'):
    sitename = 'animestar'
    # Neither 720p nor 1080p are guaranteed, but they could happen
    QUALITIES = ['360p', '480p', '540p', '720p', '1080p']
    _real_getter = 'https://api.animestar.app/api/drama?id='

    @classmethod
    def search(cls, query):
        return [
            SearchResult(
                title=i['name'],
                url='https://animestar.app/show-details/deadbeef/'+i['_id'],
                poster=i['image'],
                meta={'genre': i['genre']},
                meta_info={
                    'title_cleaned': re.sub(r'\(.*?\)', '', i['name']).strip()
                })
            for i in helpers.get('https://api.animestar.app/api/drama/search',
                                 params={'q': query},
                                 headers=_headers).json()
        ]


    def _scrape_episodes(self):
        return [
            Request('GET', 'https://api.animestar.app/api/utility/get-stream-links',
                            params={'url': i['videoUrl'], 'server': 1}
            ).prepare().url
            for i in sorted(helpers.get(self._real_getter+urlparse(self.url).path.split('/')[-1],
                                        headers=_headers).json()['episodes'],
                            key=lambda i: i['number'])
        ]

    def _scrape_metadata(self):
        resp = helpers.get(self._real_getter+urlparse(self.url).path.split('/')[-1],
                           headers=_headers).json()
        self.title = resp['name']
        self.subbed = resp['audioType'] == 'SUB'
        self.meta['names_alt'] = resp['altNames']
        self.meta['year'] = resp['releaseYear']
        self.meta['status'] = resp['tvStatus']
        self.meta['genre'] = resp['genre']
        self.meta['type'] = resp['type']
        self.meta['story'] = resp['synopsis']
        self.meta['views'] = resp['views']
        self.meta['ctime'] = datetime.fromtimestamp(resp['createdAt']/1000).strftime('%Y-%m-%d %H:%M')
        self.meta['mtime'] = datetime.fromtimestamp(resp['modifiedAt']/1000).strftime('%Y-%m-%d %H:%M')

class AnimeStarEpisode(AnimeEpisode, sitename='animestar'):
    def _get_sources(self):
        return [('no_extractor', helpers.get(self.url, headers=_headers).json()['url'])]
