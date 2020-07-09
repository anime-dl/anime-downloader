import logging
import re

from anime_downloader.sites.anime import AnimeEpisode, SearchResult, Anime
from anime_downloader.sites.exceptions import NotFoundError
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)


class AnimePaheEpisode(AnimeEpisode, sitename='animepahe'):
    QUALITIES = ['360p', '480p', '720p', '1080p']

    def _get_source(self, episode_id, server, session_id):
        # We will extract the episodes data through the animepahe api
        # which returns the available qualities and the episode sources.
        params = {
            'id': episode_id,
            'm': 'embed',
            'p': server,
            'session': session_id
        }

        episode_data = helpers.get('https://animepahe.com/api', params=params).json()
        episode_data = episode_data['data']
        sources = {}

        for info in range(len(episode_data)):
            quality = list(episode_data[info].keys())[0]
            sources[f'{quality}p'] = episode_data[info][quality]['kwik']

        if self.quality in sources:
            return (server, sources[self.quality])
        return

    def _get_sources(self):
        supported_servers = ['kwik', 'mp4upload', 'rapidvideo']
        source_text = helpers.get(self.url, cf=True).text
        sources = []

        server_list = re.findall(r'data-provider="([^"]+)', source_text)
        episode_id, session_id = re.search("getUrls\((\d+?), \"(.*)?\"", source_text).groups()

        for server in server_list:
            if server not in supported_servers:
                continue
            source = self._get_source(episode_id, server, session_id)
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

        search_results = helpers.get(cls.api_url, params=params).json()
        results = []

        for search_result in search_results['data']:
            search_result_info = SearchResult(
                title=search_result['title'],
                url=cls.base_anime_url + search_result['slug'],
                poster=search_result['poster']
            )

            logger.debug(search_result_info)
            results.append(search_result_info)

        return results

    def get_data(self):
        page = helpers.get(self.url, cf=True).text
        anime_id = re.search(r'&id=(\d+)', page).group(1)

        self.params = {
            'm': 'release',
            'id': anime_id,
            'sort': 'episode_asc',
            'page': 1
        }

        json_resp = helpers.get(self.api_url, params=self.params).json()
        self._scrape_metadata(page)
        self._episode_urls = self._scrape_episodes(json_resp)
        self._len = len(self._episode_urls)
        return self._episode_urls

    def _collect_episodes(self, ani_json, episodes=[]):
        # Avoid changing original list
        episodes = episodes[:]

        # If episodes is not an empty list we ensure that we start off
        # from the length of the episodes list to get correct episode
        # numbers
        for no, anime_ep in enumerate(ani_json, len(episodes)):
            episodes.append((no + 1, f'{self.url}/{anime_ep["id"]}',))

        return episodes

    def _scrape_episodes(self, ani_json):
        episodes = self._collect_episodes(ani_json['data'])

        if not episodes:
            raise NotFoundError(f'No episodes found for {self.url}')
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
        self.title = re.search(r'<h1>([^<]+)', data).group(1)
