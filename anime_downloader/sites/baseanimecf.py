import cfscrape
from bs4 import BeautifulSoup
import logging

from anime_downloader.sites.anime import BaseAnime
from anime_downloader.const import get_random_header

scraper = cfscrape.create_scraper()


class BaseAnimeCF(BaseAnime):
    def get_data(self):
        headers = get_random_header()
        if hasattr(self, '_referer'):
            headers['referer'] = self._referer

        r = scraper.get(self.url, headers=get_random_header())
        soup = BeautifulSoup(r.text, 'html.parser')

        self._scrape_metadata(soup)

        self._episode_urls = self._scarpe_episodes(soup)
        self._len = len(self._episode_urls)

        logging.debug('EPISODE IDS: length: {}, ids: {}'.format(
            self._len, self._episode_urls))

        self._episode_urls = [(no+1, id) for no, id in
                              enumerate(self._episode_urls)]

        return self._episode_urls
