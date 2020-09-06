import logging
import re

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)


class TopMovies(Anime, sitename='topmovies'):
    sitename = 'topmovies'
    url = f'https://{sitename}online.org/'

    @classmethod
    def search(cls, query):
        search_results = helpers.soupify(helpers.get(cls.url, params={'s': query})).select('div.title > a')
        # Cleans the year off the title for ezdl
        clean_title_regex = r'(19|20)\d{2}\s*$'
        return [
            SearchResult(
                title=i.text,
                url=i.get('href'),
                meta_info={
                    'title_cleaned': re.sub(clean_title_regex, "", i.text.strip()).strip()
                })
            for i in search_results
        ]

    def _scrape_episodes(self):
        if '/movies/' in self.url:
            return [self.url]
        soup = helpers.soupify(helpers.get(self.url))
        elements = soup.select('div.episodiotitle > a')
        return [i.get('href') for i in elements[::-1]]

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.select('div.data > h1')[0].text


class TopMoviesEpisode(AnimeEpisode, sitename='topmovies'):
    def _get_sources(self):
        soup = helpers.soupify(helpers.get(self.url))
        player = soup.select_one('li#player-option-1')
        if not player:
            logger.error('Unable to find player.')
            return ''

        data_post = player['data-post']
        data_nume = player.get('data-nume', 1)
        data_type = player['data-type']

        data = helpers.post('https://topmoviesonline.org/wp-admin/admin-ajax.php',
                            referer=self.url, data={
                                'action': 'doo_player_ajax',
                                'post': data_post,
                                'nume': data_nume,
                                'type': data_type
                            })
        src = helpers.soupify(data).select_one('iframe')['src']
        return [('ezlink', src)]
