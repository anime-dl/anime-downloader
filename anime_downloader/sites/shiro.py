import logging
import re
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)


def get_token():
    r = helpers.get('https://shiro.is').text
    script = 'https://shiro.is' + re.search(r'src\=\"(\/static\/js\/main\..*?)\"', r)[1]  # noqa
    script = helpers.get(script).text
    token = re.search(r'token\:\"(.*?)\"', script)[1]
    return token


class Shiro(Anime, sitename='shiro'):
    sitename = 'shiro'

    @classmethod
    def search(cls, query):
        cls.token = get_token()
        params = {
            'search': query,
            'token': cls.token
        }
        results = helpers.get('https://ani.api-web.site/advanced', params=params).json()['data']  # noqa
        if 'nav' in results:
            results = results['nav']['currentPage']['items']
            search_results = [
                SearchResult(
                    title=i['name'],
                    url='https://shiro.is/anime/' + i['slug'],
                    poster='https://ani-cdn.api-web.site/' + i['image'],
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
            api_link = 'https://ani.api-web.site/anime-episode/slug/' + slug
            r = helpers.get(api_link, params={'token': self.token}).json()
            slug = r['data']['anime_slug']
        api_link = 'https://ani.api-web.site/anime/slug/' + slug
        r = helpers.get(api_link, params={'token': self.token}).json()
        if r['status'] == 'Found':
            episodes = r['data']['episodes']
            episodes = [
                'https://ani.googledrive.stream/vidstreaming/vid-ad/' + x['videos'][0]['video_id']  # noqa
                for x in episodes
            ]
            return episodes
        else:
            return []

    def _scrape_metadata(self):
        self.token = get_token()
        slug = self.url.split('/')[-1]
        if 'episode' in slug:
            api_link = 'https://ani.api-web.site/anime-episode/slug/' + slug
            r = helpers.get(api_link, params={'token': self.token}).json()
            slug = r['data']['anime_slug']
        api_link = 'https://ani.api-web.site/anime/slug/' + slug
        r = helpers.get(api_link, params={'token': self.token}).json()
        self.title = r['data']['name']


class ShiroEpisode(AnimeEpisode, sitename='shiro'):
    def _get_sources(self):
        r = helpers.get(self.url).text
        link = re.search(r'\"file\"\:\"(.*?)\"', r)[1]
        return [('no_extractor', link)]
