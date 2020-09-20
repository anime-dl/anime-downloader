import json
import requests

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers


class AnimeOnline(Anime, sitename='animeonline360'):

    sitename = 'animeonline360'

    @classmethod
    def search(cls, query):
        try:
            r = helpers.soupify(helpers.get('https://animeonline360.me/', params={'s': query})).select('div.title')
            results = [{"title": x.text, "url": x.a['href']} for x in r]
            search_results = [
                SearchResult(
                    title=i['title'],
                    url=i['url'],
                    meta_info={
                        'version_key_dubbed': 'Dubbed',
                        'version_key_subbed': 'Subbed',
                    }
                )
                for i in results
            ]

            return search_results
        except:
            return ""

    def _scrape_episodes(self):
        data = helpers.soupify(helpers.get(self.url)).select('div.episodiotitle > a')
        return [i.get('href') for i in data[::-1]]

    def _scrape_metadata(self):
        self.title = helpers.soupify(helpers.get(self.url)).title.text.split('|')[0].strip().title()


class AnimeOnlineEpisode(AnimeEpisode, sitename='animeonline360'):
    def _get_sources(self):
        return [('animeonline360', self.url)]
