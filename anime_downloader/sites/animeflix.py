from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers


class AnimeFlix(Anime, sitename='animeflix'):
        """
        Site :https://animeflix.io/

        """
        sitename = 'animeflix'
        search_url = 'https://www.animeflix.io/api/search'
        anime_url = 'https://www.animeflix.io/shows'
        episodeList_url = 'https://www.animeflix.io/api/anime-schema'
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
            self.slug = self.url.strip('/').split('/')[-1]
            episodes = helpers.get(self.episodeList_url,
                                   params={'slug': self.slug}).json()
            return [ self.anime_url + episode['url'] for episode in episodes['episodes'] ]
        
        def _scrape_metadata(self):
            meta = helpers.get(self.meta_url, 
                               params={'slug': self.slug}).json()
            self.title = meta['data']['title']



class AnimeFlixEpisode(AnimeEpisode, sitename='animeflix'):
        episodeId_url = 'https://animeflix.io/api/episode'
        stream_url = 'https://animeflix.io/api/videos?episode_id'
        anime_url = 'https://www.animeflix.io/shows'

        def _get_sources(self):
            episode = helpers.get(self.episodeId_url,
                                  params={'episode_num': self.ep_no, 'slug': self.url.strip('/').split('/')[-2]}).json()
            id = episode['data']['current']['id']
            download_link = helpers.get(
                f'{self.stream_url}={id}').json()[0]['file']
            return [('no_extractor',download_link)]
