from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import json
import re
import logging

logger = logging.getLogger(__name__)


def get_token():
    r = helpers.get('https://animefrenzy.org').text
    script = 'https://animefrenzy.org' + re.search(r'src\=\"(\/static\/js\/main\..*?)\"', r)[1]  # noqa
    script = helpers.get(script).text
    token = re.search(r'token\:\"(.*?)\"', script)[1]
    return token


class AnimeFrenzy(Anime, sitename='animefrenzy'):
    sitename = 'animefrenzy'
    token = get_token()

    @classmethod
    def search(cls, query):
        results = helpers.get("https://moo.yare.wtf/advanced", params={"search": query, "token": cls.token}).json()['data']  # noqa
        if 'nav' in results:
            results = results['nav']['currentPage']['items']
            search_results = [
                SearchResult(
                    title=i['name'],
                    url='https://animefrenzy.org/anime/' + i['slug'],
                    poster='https://moo.yare.wtf/' + i['image'],
                    meta={'year': i['year']},
                    meta_info={
                        'version_key_dubbed': '(Sub)' if i['language'] == 'subbed' else '(Dub)'  # noqa
                    }
                )
                for i in results
            ]
            search_results = sorted(search_results, key=lambda x: int(x.meta['year']))
            return search_results
        else:
            return []

    def _scrape_episodes(self):
        self.token = get_token()
        slug = self.url.split('/')[-1]
        if 'episode' in slug:
            api_link = 'https://moo.yare.wtf/anime-episode/slug/' + slug
            r = helpers.get(api_link, params={'token': self.token}).json()
            slug = r['data']['anime_slug']

        api_link = 'https://moo.yare.wtf/anime/slug/' + slug
        r = helpers.get(api_link, params={'token': self.token}).json()
        if r['status'] == 'Found':
            episodes = r['data']['episodes']
            episodes = [
                'https://moo.yare.wtf/vidstreaming/animefrenzy/' + x['videos'][0]['video_id']  # noqa
                for x in episodes
            ]
            return episodes
        else:
            return []

    def _scrape_metadata(self):
        slug = self.url.split('/')[-1]
        if 'episode' in slug:
            api_link = 'https://moo.yare.wtf/anime-episode/slug/' + slug
            r = helpers.get(api_link, params={'token': self.token}).json()
            slug = r['data']['anime_slug']
        api_link = 'https://moo.yare.wtf/anime/slug/' + slug
        r = helpers.get(api_link, params={'token': self.token}).json()
        self.title = r['data']['name']


class AnimeFrenzyEpisode(AnimeEpisode, sitename='animefrenzy'):
    def _get_sources(self):
        r = helpers.get(self.url).text
        link = re.search(r'\"file\"\:\"(.*?)\"', r)[1]
        return [('no_extractor', link)]
