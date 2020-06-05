from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import logging

logger = logging.getLogger(__name__)

class AnimeFlix(Anime, sitename='animeflix'):
        """
        Nice things
        Siteconfig
        ----------
        server: Primary server to use (Default: AUEngine)
        fallback_servers: Recorded working servers which is used if the primary server cannot be found (FastStream works, but downloads m3u8 files)
        version: sub/dub, language
        """
        sitename = 'animeflix'
        search_url = 'https://animeflix.io/api/search'
        anime_url = 'https://animeflix.io/shows'
        episodeList_url = 'https://animeflix.io/api/anime-schema'
        meta_url = 'https://animeflix.io/api/anime/detail'
        QUALITIES = ['360p', '480p', '720p', '1080p']

        @classmethod
        def search(cls, query):
            search_results = helpers.get(cls.search_url,
                                        params={'q' : query}).json()
            search_results = [
                SearchResult(
                    title=result['title'],
                    url=f'{cls.anime_url}/{result["slug"]}',
                )
                for result in search_results.get('data',[])
            ]

            return search_results
        
        def _scrape_episodes(self):
            # TODO: find a better way to do splits
            # find a way to pass some values within the class
            episodes = helpers.get(self.episodeList_url,
                                   params={'slug': self.slug}).json()

            if episodes.get('@type','') == 'Movie': #different response if movies
                return [episodes['potentialAction']['target']]
            return [ self.anime_url + episode['url'] for episode in episodes['episodes'] ]

        def _scrape_metadata(self):
            self.slug = self.url.strip('/').split('/')[-1]
            meta = helpers.get(self.meta_url, 
                               params={'slug': self.slug}).json()
            self.title = meta['data']['title']
            logger.debug(self.title)


class AnimeFlixEpisode(AnimeEpisode, sitename='animeflix'):
        episodeId_url = 'https://animeflix.io/api/episode'
        stream_url = 'https://animeflix.io/api/videos?episode_id'
        anime_url = 'https://www.animeflix.io/shows'

        def _get_sources(self):
            version = self.config['version'] 
            server = self.config['server']
            fallback = self.config['fallback_servers']

            episode = helpers.get(self.episodeId_url,
                                  params={'episode_num': self.ep_no, 'slug': self.url.strip('/').split('/')[-2]}).json()
            _id = episode['data']['current']['id']
            download_link = helpers.get(
                f'{self.stream_url}={_id}').json()

            for a in download_link: #Testing sources with selected language and provider
                if a['lang'] == self.config['version']:
                    if a['provider'] == self.config['server']:
                        return [('no_extractor', a['file'],)]

            logger.debug('Preferred server %s not found. Trying all supported servers in selected language.',server)

            for a in download_link: #Testing sources with selected language
                if a['lang'] == self.config['version']:
                    return [('no_extractor', a['file'],)]

            logger.debug('No %s servers found, trying all servers',self.config['version'])
            return[('no_extractor', download_link[0]['file'],)]
