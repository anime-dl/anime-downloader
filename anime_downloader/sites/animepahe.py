import logging
import re

from anime_downloader.sites.anime import AnimeEpisode, SearchResult, Anime
from anime_downloader.sites.exceptions import NotFoundError
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)


class AnimePahe(Anime, sitename='animepahe'):
    sitename = 'animepahe'
    api_url = 'https://animepahe.com/api'

    @classmethod
    def search(cls, query):
        params = {
            'l': 8,
            'm': 'search',
            'q': query
        }

        search_results = helpers.get(cls.api_url, params=params).json()
        if search_results['total'] == []:
            return []

        return [
            SearchResult(
                title=result['title'] + " (" + result['type'] + ")",
                url="https://animepahe.com/anime/TITLE!" + result['title'] + " (" + result['type'] + ")" + '!TITLE/' + result['session'] + "/" + str(result['id']),  # noqa
                poster=result['poster']
            )
            for result in search_results['data']
        ]

    def _scrape_episodes(self):
        attr = self.url.split('/')
        session = attr[-2]
        id_ = attr[-1]
        page = 1
        headers = {'referer': 'https://animepahe.com/'}

        apiUri = self.api_url + '?m=release&id=' + id_ + '&sort=episode_asc&page='
        jsonResponse = helpers.get(apiUri + str(page), headers=headers).json()
        lastPage = jsonResponse['last_page']
        perPage = jsonResponse['per_page']
        total = jsonResponse['total']
        ep = 1
        episodes = []

        if (lastPage == 1 and perPage > total):
            for epi in jsonResponse['data']:
                episodes.append(
                    f'{self.api_url}?m=links&id={epi["anime_id"]}&session={epi["session"]}&p=kwik!!TRUE!!')
        else:
            stop = False
            for page in range(lastPage):
                if stop:
                    break
                for i in range(perPage):
                    if ep <= total:
                        episodes.append(
                            f'{self.api_url}?m=release&id={id_}&sort=episode_asc&page={page+1}&ep={ep}!!FALSE!!')
                        ep += 1
                    else:
                        stop = True
                        break
        return episodes

    def _scrape_metadata(self):
        self.title = re.findall(r"TITLE!(.*?)!TITLE", self.url)[0]


class AnimePaheEpisode(AnimeEpisode, sitename='animepahe'):
    def _get_sources(self):
        if '!!TRUE!!' in self.url:
            self.url = self.url.replace('!!TRUE!!', '')
        else:
            headers = {'referer': 'https://animepahe.com/'}
            regex = r"\&ep\=(\d+)\!\!FALSE\!\!"
            episodeNum = int(re.findall(regex, self.url)[0])
            self.url = re.sub(regex, '', self.url)
            jsonResponse = helpers.get(self.url, headers=headers).json()

            ep = None
            for episode in jsonResponse['data']:
                if int(episode['episode']) == episodeNum:
                    ep = episode
            if ep:
                self.url = 'https://animepahe.com/api?m=links&id=' + str(ep['anime_id']) + '&session=' + ep['session'] + '&p=kwik'  # noqa
            else:
                raise NotFoundError

        episode_data = helpers.get(self.url).json()

        data = episode_data['data']
        qualities = [x + 'p' for f in data for x in f]

        sources_list = [
           f[x]['kwik_adfly'] for f in data for x in f
        ]

        for i, quality in enumerate(qualities):
            if self.quality == quality:
                return [("kwik", sources_list[i])]

        return [("kwik", x) for x in sources_list]
