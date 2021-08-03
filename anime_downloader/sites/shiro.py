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

def get_api_url():
    return "https://tapi.shiro.is"

class Shiro(Anime, sitename='shiro'):
    sitename = 'shiro'

    @classmethod
    def search(cls, query):
        cls.token = get_token()
        cls.api_url = get_api_url()

        params = {
            'search': query,
            'token': cls.token
        }
        results = helpers.get(f'{cls.api_url}/advanced', params=params).json()['data']  # noqa
        if 'nav' in results:
            results = results['nav']['currentPage']['items']
            search_results = [
                SearchResult(
                    title=i['name'],
                    url='https://shiro.is/anime/' + i['slug'],
                    poster=f'{cls.api_url}/' + i['image'],
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
        self.api_url = get_api_url()

        slug = self.url.split('/')[-1]
        if 'episode' in slug:
            api_link = f'{self.api_url}/anime-episode/slug/' + slug
            r = helpers.get(api_link, params={'token': self.token}).json()
            slug = r['data']['anime_slug']
        api_link = f'{self.api_url}/anime/slug/' + slug
        r = helpers.get(api_link, params={'token': self.token}).json()
        if r['status'] == 'Found':
            episodes = r['data']['episodes']
            episodes = [
                "https://cherry.subsplea.se/" + x['videos'][0]['video_id']  # noqa
                for x in episodes
            ]
            return episodes
        else:
            return []

    def _scrape_metadata(self):
        self.token = get_token()
        self.api_url = get_api_url()


        slug = self.url.split('/')[-1]
        if 'episode' in slug:
            api_link = f'{self.api_url}/anime-episode/slug/' + slug
            r = helpers.get(api_link, params={'token': self.token}).json()
            slug = r['data']['anime_slug']
        api_link = f'{self.api_url}/anime/slug/' + slug
        r = helpers.get(api_link, params={'token': self.token}).json()
        self.title = r['data']['name']


class ShiroEpisode(AnimeEpisode, sitename='shiro'):
    def _get_sources(self):
        r = helpers.get(self.url, referer="https://shiro.is/").text
        link = re.search(r'source\s+src=\"(.*?)\"', r)[1]
        return [('no_extractor', link)]
