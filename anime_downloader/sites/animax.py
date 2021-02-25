import logging
import re
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)


class Animax(Anime, sitename='animax'):
    sitename = 'animax'

    @classmethod
    def search(cls, query):
        params = {
            'q': query,
            'c': 'search'
        }
        soup = helpers.soupify(helpers.get('https://animax.to/', params=params).text)
        search_results = soup.select_one('.columns2').select('h1')
        search_results = [
            SearchResult(
                title=i.text.strip(),
                url='https://animax.to' + i.a['href'],
                poster='https://animax.to' + i.select_one('img')['src'],
                meta_info={
                    'version_key_dubbed': '(Sub)' if ' (Sub)' in i.text.strip() else '(Dub)'  # noqa
                }
            )
            for i in search_results
        ]
        return search_results

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url).text)
        return ['https://animax.to' + x.select_one('a')['href'] for x in soup.select('tbody > tr')][::-1]

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url).text)
        self.title = soup.find('meta', property='og:title')['content'].split('anime | Watch')[0].strip()


class AnimaxEpisode(AnimeEpisode, sitename='animax'):
    def _get_sources(self):
        regex = r"file: \"(.*?)\""
        html = helpers.get(self.url).text
        try:
            stream = re.search(regex, html)[1].replace('/m3u8/', 'https://animax.to/m3u8/')
        except:
            return []
        return [('no_extractor', stream)]
