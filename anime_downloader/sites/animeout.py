import logging
import re

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)


class AnimeOut(Anime, sitename='animeout'):
    sitename = 'animeout'
    url = f'https://{sitename}.xyz/'

    @classmethod
    def search(cls, query):
        search_results = helpers.soupify(helpers.get(
            cls.url, params={'s': query})).select('h3.post-title > a')
        # Removes the unneded metadata from the title
        # Used by MAL matcher
        clean_title_regex = r'\(.*?\)'
        return [
            SearchResult(
                title=i.text,
                url=i.get('href'),
                meta_info={
                    'title_cleaned': re.sub(clean_title_regex, "", i.text).strip()
                })
            for i in search_results
        ]

    def _scrape_episodes(self):
        # Only uses the direct download links for consistency.
        soup = helpers.soupify(helpers.get(self.url))
        elements = soup.select('article.post a')
        episodes = [i.get('href')
                    for i in elements if 'Direct Download' in i.text]

        filters = [self.quality, "1080p", "720p"]
        quality_filtered = []

        for _filter in filters:
            if not quality_filtered:
                quality_filtered = [x for x in episodes if _filter in x]
            else:
                break

        return episodes if not quality_filtered else quality_filtered

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.select('h1.page-title')[0].text


class AnimeOutEpisode(AnimeEpisode, sitename='animeout'):
    def _get_sources(self):
        # Should probably be moved to a separate extractor.
        # Note that --play doesn't seem to work on generated links.
        soup = helpers.soupify(helpers.get(self.url))
        link = soup.select('div.Center > p > h2 > a')[0].get('href')
        logger.debug(f'Link: {link}')
        # Note that this [2] can get outdated.
        script = helpers.soupify(helpers.get(link)).select('script')[2]
        url = re.search(r'http[^"]*', str(script)).group()
        return [('no_extractor', url,)]
