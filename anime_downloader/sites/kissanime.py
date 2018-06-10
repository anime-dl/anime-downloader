import cfscrape
from anime_downloader.sites.anime import BaseEpisode
from anime_downloader.sites.baseanimecf import BaseAnimeCF
from anime_downloader.sites.exceptions import NotFoundError
from anime_downloader.sites import util
from bs4 import BeautifulSoup
import re
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


class KissanimeEpisode(BaseEpisode):
    QUALITIES = ['360p', '480p', '720p']
    _base_url = 'http://kissanime.ru'
    VERIFY_HUMAN = True

    def getData(self):
        url = self._base_url+self.episode_id
        logging.debug('Calling url: {}'.format(url))
        r = scraper.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')

        if self.VERIFY_HUMAN:
            episode_url = soup.find('form',
                                    {'id': 'formVerify'}).find('a')['href']
        else:
            episode_url = self.episode_id

        ret = scraper.get(self._base_url+episode_url)
        data = self._scrape_episode(ret)

        self.stream_url = data['stream_url']
        self.title = data['title']
        self.image = data['image']

    def _scrape_episode(self, response):

        rapid_re = re.compile(r'iframe.*src="https://(.*?)"')
        rapid_url = rapid_re.findall(response.text)[0]

        data = util.get_stream_url_rapidvideo('https://'+rapid_url,
                                              self.quality)

        return data


class Kissanime(BaseAnimeCF):
    sitename = 'kissanime'
    QUALITIES = ['360p', '480p', '720p']
    _episodeClass = KissanimeEpisode

    def _getEpisodeUrls(self, soup):
        ret = soup.find('table', {'class': 'listing'}).find_all('a')
        ret = [str(a['href']) for a in ret]

        if ret == []:
            err = 'No episodes found in url "{}"'.format(self.url)
            args = [self.url]
            raise NotFoundError(err, *args)

        ret = ret[::-1]
        return ret

    def _getMetadata(self, soup):
        info_div = soup.find('div', {'class': 'barContent'})
        self.title = info_div.find('a', {'class': 'bigChar'}).text
