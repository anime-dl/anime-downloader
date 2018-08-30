import json
import re
import cfscrape
import logging
from bs4 import BeautifulSoup

from anime_downloader.sites.anime import BaseAnime, BaseEpisode
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

        # TODO: Clean this up. Why it looks like this, I don't know.
        ret_1 = [(name, url) for name, url in ret if name in ['stream.moe']]
        ret_1 += [(name, url) for name, url in ret if name == 'rapidvideo']
        ret_1 += [(name, url) for name, url in ret if name == 'mp4upload']

        logging.debug(ret_1)

        return ret_1


class Masterani(BaseAnime):
    sitename = 'masterani'
    QUALITIES = ['360p', '480p', '720p', '1080p']
    _api_url = 'https://www.masterani.me/api/anime/{}/detailed'
    _episodeClass = MasteraniEpisode

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
