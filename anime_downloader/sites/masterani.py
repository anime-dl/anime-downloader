import json
import re
import cfscrape
import logging
import requests
from bs4 import BeautifulSoup

from anime_downloader import util
from anime_downloader.sites.anime import BaseAnime, BaseEpisode, SearchResult
from anime_downloader.const import desktop_headers

scraper = cfscrape.create_scraper()


class MasteraniEpisode(BaseEpisode):
    QUALITIES = ['360p', '480p', '720p', '1080p']

    def _get_sources(self):
        logging.debug('[cfscrape] Calling {}'.format(self.url))
        res = scraper.get(self.url, headers=desktop_headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        # Masterani changed
        # sources_re = re.compile(r'mirrors:.*?(\[.*?\])')
        quality = int(self.quality[:-1])

        sources = json.loads(soup.find('video-mirrors')[':mirrors'])
        logging.debug('Found sources {}. filtering...'.format(sources))

        ret = []
        for source in sources:
            url = source['host']['embed_prefix'] + source['embed_id']

            if source['host']['name'].lower() == 'rapidvideo':
                ret.append((source['host']['name'].lower(), url))
                continue

            if source['quality'] != quality:
                continue

            if source['host']['embed_suffix']:
                url += source['host']['embed_suffix']

            ret.append((source['host']['name'].lower(), url))

        sources = ['stream.moe', 'rapidvideo', 'mp4upload']
        ret = [(name, url) for name, url in ret if name in sources]

        logging.debug(ret)

        return ret


class Masterani(BaseAnime):
    sitename = 'masterani'
    QUALITIES = ['360p', '480p', '720p', '1080p']
    _api_url = 'https://www.masterani.me/api/anime/{}/detailed'
    _episodeClass = MasteraniEpisode

    @classmethod
    def search(cls, query):
        r = util.get_json('https://masterani.me/api/anime/filter?',
                          {'search': query, 'order': 'relevance_desc'})

        search_result = r['data']

        ret = []

        logging.debug('Search results')

        for item in search_result:
            s = SearchResult(
                title=item['title'],
                url='https://masterani.me/anime/info/{}'.format(item['slug']),
                poster='https://cdn.masterani.me/{}{}'.format(
                    item['poster']['path'], item['poster']['file']
                )
            )
            logging.debug(s)
            ret.append(s)

        return ret


    def get_data(self):
        anime_id = self.url.split('info/')[-1].split('-')[0]
        url = self._api_url.format(anime_id)
        res = scraper.get(url, headers=desktop_headers)
        try:
            res = res.json()
        except Exception:
            logging.debug('Error with html {}'.format(res.text))
            raise
        base_url = 'https://www.masterani.me/anime/watch/{}'.format(
            res['info']['slug']) + '/'

        episode_urls = []
        for episode in res['episodes']:
            url = base_url + episode['info']['episode']
            episode_urls.append((episode['info']['episode'], url))

        self._episode_urls = episode_urls
        self.meta = res['info']
        self.title = self.meta['title']
        self._len = len(self._episode_urls)

        return self._episode_urls
