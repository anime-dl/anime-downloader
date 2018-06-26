from anime_downloader.sites.anime import BaseAnime, BaseEpisode
import json
import requests

# class MasteraniEpisode(BaseEpisode):


class Masterani(BaseAnime):
    sitename = 'masterani'
    QUALITIES = ['360p', '480p', '720p']
    _api_url = 'https://www.masterani.me/api/anime/{}/detailed'

    def get_data(self):
        anime_id = self.url.split('info/')[-1].split('-')[0]
        url = self._api_url.format(anime_id)
        res = requests.get(url)
        res = res.json()

        self.meta = res['info']
