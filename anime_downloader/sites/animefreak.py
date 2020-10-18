import re

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites.exceptions import NotFoundError
from anime_downloader.sites import helpers


class AnimeFreak(Anime, sitename='animefreak'):
    sitename = 'animefreak'
    search_url = f'https://www.{sitename}.tv/search/topSearch'
    anime_url = 'https://www.animefreak.tv/watch'
    QUALITIES = ['360p', '480p', '720p', '1080p']

    @classmethod
    def search(cls, query):
        search_results = helpers.get(cls.search_url,
                                     params={'q': query}).json()
        search_results = [
            SearchResult(
                title=result['name'],
                url=f'{cls.anime_url}/{result["seo_name"]}')
            for result in search_results.get('data', [])
        ]

        return search_results

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        # Negative index for episode links in cases where full episode
        # list is available or if not default to usual episode list
        episode_links = soup.select('ul.check-list')[-1].select('li a')
        return [a.get('href') for a in episode_links][::-1]

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.select_one('.anime-title').text


class AnimeFreakEpisode(AnimeEpisode, sitename='animefreak'):
    def _get_sources(self):
        page = helpers.get(self.url).text
        source_re = re.compile(r'loadVideo.+file: "([^"]+)', re.DOTALL)
        match = source_re.findall(page)

        # E.g. episode-946
        url_end = self.url.split("/")[-1]

        # To ensure that it isn't a special/preview or something
        logger.info(url_end)
        if "episode" in url_end:
            episode_number_regexed = re.search("\d+", url_end)
            # Just in case we don't have the ep number in url_end for some unexpected reason
            if episode_number_regexed:
                self.ep_no = episode_number_regexed.group()
                logger.info(self.ep_no)

        if not match:
            raise NotFoundError(f'Failed to find video url for {self.url}')
        return [('no_extractor', match[0],)]
