from anime_downloader.sites.anime import BaseAnime, BaseEpisode
import json
import cfscrape
import requests

scraper = cfscrape.create_scraper()


class MasteraniEpisode(BaseEpisode):
    QUALITIES = ['360p', '480p', '720p']

    # def _get_sources(self):


class Masterani(BaseAnime):
    sitename = 'masterani'
    QUALITIES = ['360p', '480p', '720p']
    _api_url = 'https://www.masterani.me/api/anime/{}/detailed'
    _episodeClass = MasteraniEpisode

    @classmethod
    def get_data(self):
        anime_id = self.url.split('info/')[-1].split('-')[0]
        url = self._api_url.format(anime_id)
        res = scraper.get(url).json()
        base_url = 'https://www.masterani.me/anime/watch/{}'.format(
            res['info']['slug']) + '/'

        episode_urls = []
        for episode in res['episodes']:
            url = base_url + episode['info']['episode']
            episode_urls.append(url)

        self._episodeIds = episode_urls
        self.meta = res['info']

        return self._episodeIds
