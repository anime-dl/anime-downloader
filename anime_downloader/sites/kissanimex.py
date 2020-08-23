from anime_downloader.sites import helpers
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
import logging

logger = logging.getLogger(__name__)

class KissAnimeX(Anime, sitename = 'kissanimex'):
    sitename = "kissanimex"

    @classmethod
    def search(cls, query):
        url = 'https://kissanimex.com/search?url=search'
        soup = helpers.soupify(helpers.get(url, params={'q': query}))
        items = soup.select('td > a')
        search_results = [
                SearchResult(
                    title = x.text,
                    url = 'https://kissanimex.com' + x['href']
                    )
                for x in items
                ]
        return search_results

    def _scrape_episodes(self):
        r = helpers.get(self.url).text
        soup = helpers.soupify(r)

        # Allows fallback from both dub -> sub and sub -> dub
        # This makes it possible to download pokemon (for example) without having to change config.
        subbed = self.config['version'] != 'dubbed'
        subbed_converter = {
            True:'div#episodes-sub',
            False:'div#episodes-dub',
        }

        eps = soup.select_one(subbed_converter.get(subbed)).select('td > a')
        if not eps:
            logger.info('No episodes in selected language, falling back.')
            eps = soup.select_one(subbed_converter.get(not subbed)).select('td > a')
            if not eps:
                logger.info('No episodes found.')
                return []

        episodes = ['https://kissanimex.com' + x.get('href') for x in eps][::-1]
        return episodes

    def _scrape_metadata(self):
        self.title = helpers.soupify(helpers.get(self.url).text).select_one('a.bigChar').text

class KissAnimeXEpisode(AnimeEpisode, sitename='kissanimex'):
    def _get_sources(self):
        r = helpers.get(self.url).text
        sources = helpers.soupify(r).select('div.host#menu > a')
        sources = [x['data-video-link'] for x in sources]

        map_extractors = {
            'vidstream': 'vidstream'
        }
        for source in sources:
            for extractor in map_extractors:
                if extractor in source:
                    return [(extractor, source)]
        return ''
