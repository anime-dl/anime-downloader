import cfscrape
from anime_downloader.sites.anime import BaseAnime
from bs4 import BeautifulSoup
import logging

scraper = cfscrape.create_scraper()

mobile_headers = {
    'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0_1 like Mac OS X) \
                  AppleWebKit/604.1.38 (KHTML, like Gecko) \
                  Version/11.0 Mobile/15A402 Safari/604.1"
}

desktop_headers = {
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 \
Firefox/56.0"
}

scraper = cfscrape.create_scraper()


class BaseAnimeCF(BaseAnime):
    def getEpisodes(self):
        self._episodeIds = []
        r = scraper.get(self.url, headers=desktop_headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        self._getMetadata(soup)

        self._episodeIds = self._getEpisodeUrls(soup)
        self._len = len(self._episodeIds)

        logging.debug('EPISODE IDS: length: {}, ids: {}'.format(
            self._len, self._episodeIds))

        self._episodeIds = [(no+1, id) for no, id in
                            enumerate(self._episodeIds)]

        return self._episodeIds
