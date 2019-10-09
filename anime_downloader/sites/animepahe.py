import logging
import re

from anime_downloader.sites.anime import AnimeEpisode, SearchResult, Anime
from anime_downloader.sites.exceptions import NotFoundError
from anime_downloader.sites import helpers
from anime_downloader import util

logger = logging.getLogger(__name__)


class AnimePaheEpisode(AnimeEpisode, sitename='animepahe'):
    QUALITIES = ['360p', '480p', '720p', '1080p']

    def _get_source(self, episode_id, server):

        # We will extract the episodes data through the animepahe api
        # which returns the available qualities and the episode sources.
        params = {
            'id': episode_id,
            'm': 'embed',
            'p': server
        }

        episode = helpers.get('https://animepahe.com/api', params=params).json()
        sources = episode['data'][episode_id]

        if self.quality in sources:
            return (server, sources[self.quality]['url'])
        return

    def _get_sources(self):

        supported_servers = ['kwik','mp4upload','rapidvideo']
        episode_id = self.url.rsplit('/', 1)[-1]

        sourcetext = helpers.get(self.url, cf=True).text
        sources = []
        serverlist = re.findall(r'data-provider="([^"]+)', sourcetext)
        for server in serverlist:
            if server not in supported_servers:
                continue
            source =  self._get_source(episode_id, server)
            if source:
                sources.append(source)

        if sources:
            return sources
        raise NotFoundError

class AnimePahe(Anime, sitename='animepahe'):
    sitename = 'animepahe'
    api_url = 'https://animepahe.com/api'
    base_anime_url = 'https://animepahe.com/anime/'
    QUALITIES = ['360p', '480p', '720p', '1080p']
    _episodeClass = AnimePaheEpisode

    @classmethod
    def search(cls, query):
        params = {
            'l': 8,
            'm': 'search',
            'q': query
        }

        search_results = helpers.get(
                            cls.api_url,
                            params=params,
                         ).json()

        results = []

        for search_result in search_results['data']:
            search_result_info = SearchResult(
                title=search_result['title'],
                url=cls.base_anime_url + search_result['slug'],
                poster=search_result['image']
            )

            logger.debug(search_result_info)
            results.append(search_result_info)

        return results

    def get_data(self):
        # Extract anime id from page, using this shoddy approach as
        # I have neglected my regular expression skills to the point of
        # disappointment
        resp = helpers.get(self.url, cf=True).text
        first_search = '$.getJSON(\'/api?m=release&id='
        last_search = '&l=\' + limit + \'&sort=\' + sort + \'&page=\' + page'

        anime_id = (resp[resp.find(first_search)+len(first_search):
                         resp.find(last_search)])

        self.params = {
            'm': 'release',
            'id': anime_id,
            'sort': 'episode_asc',
            'page': 1
        }

        resp = helpers.get(self.api_url, params=self.params).json()

        self._scrape_metadata(resp['data'])

        self._episode_urls = self._scrape_episodes(resp)
        self._len = len(self._episode_urls)

        return self._episode_urls

    def _collect_episodes(self, ani_json, episodes=[]):
        # Avoid changing original list
        episodes = episodes[:]

        # If episodes is not an empty list we ensure that we start off
        # from the length of the episodes list to get correct episode
        # numbers
        for no, anime_ep in enumerate(ani_json, len(episodes)):
            episodes.append(
                (no+1, self.url + '/' + str(anime_ep['id']),)
            )

        return episodes

    def _scrape_episodes(self, ani_json):
        episodes = self._collect_episodes(ani_json['data'])

        if not episodes:
            raise NotFoundError(
                'No episodes found in url "{}"'.format(self.url),
                self.url
                )
        else:
            # Check if other pages exist since animepahe only loads
            # first page and make subsequent calls to the api for every
            # page
            start_page = ani_json['current_page'] + 1
            end_page = ani_json['last_page'] + 1

            for i in range(start_page, end_page):
                self.params['page'] = i
                resp = helpers.get(self.api_url, params=self.params).json()

                episodes = self._collect_episodes(resp['data'], episodes)

        return episodes

    def _scrape_metadata(self, data):
        self.title = data[0]['anime_title']
