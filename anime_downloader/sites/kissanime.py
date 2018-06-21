import cfscrape
from bs4 import BeautifulSoup
import re
import logging

from anime_downloader.sites.anime import BaseEpisode, SearchResult
from anime_downloader.sites.baseanimecf import BaseAnimeCF
from anime_downloader.sites.exceptions import NotFoundError
from anime_downloader.sites import util
from anime_downloader.const import desktop_headers


scraper = cfscrape.create_scraper()


class KissanimeEpisode(BaseEpisode):
    QUALITIES = ['360p', '480p', '720p']
    _base_url = 'http://kissanime.ru'
    VERIFY_HUMAN = True

    def getData(self):
        episode_url = self._base_url+self.episode_id+'&s=rapidvideo'
        logging.debug('Calling url: {}'.format(episode_url))

        ret = scraper.get(episode_url)
        data = self._scrape_episode(ret)

        self.stream_url = data['stream_url']
        self.title = data['title']
        self.image = data['image']

    def _scrape_episode(self, response):

        rapid_re = re.compile(r'iframe.*src="https://(.*?)"')
        rapid_url = rapid_re.findall(response.text)[0]

        data = util.get_stream_url_rapidvideo('https://'+rapid_url,
                                              self.quality,
                                              headers=desktop_headers)

        return data


class Kissanime(BaseAnimeCF):
    sitename = 'kissanime'
    QUALITIES = ['360p', '480p', '720p']
    _episodeClass = KissanimeEpisode

    @classmethod
    def search(cls, query):
        res = scraper.post(
            'http://kissanime.ru/Search/Anime',
            data={
                'type': 'Anime',
                'keyword': query,
            },
            headers=desktop_headers,
        )

        soup = BeautifulSoup(res.text, 'html.parser')

        if soup.title.text.strip().lower() != "find anime":
            return [SearchResult(
                title=soup.find('a', 'bigChar').text,
                url='https://kissanime.ru'+soup.find('a', 'bigChar').get('href'),
                poster='',
            )]

        searched = [s for i, s in enumerate(soup.find_all('td')) if not i % 2]

        ret = []
        for res in searched:
            res = SearchResult(
                title=res.text.strip(),
                url='https://kissanime.ru'+res.find('a').get('href'),
                poster='',
            )
            logging.debug(res)
            ret.append(res)

        return ret

    def _getEpisodeUrls(self, soup):
        ret = soup.find('table', {'class': 'listing'}).find_all('a')
        ret = [str(a['href']) for a in ret]
        logging.debug('Unfiltered episodes : {}'.format(ret))
        filter_list = ['opening', 'ending', 'special', 'recap']
        ret = list(filter(
            lambda x: not any(s in x.lower() for s in filter_list), ret
        ))
        logging.debug('Filtered episodes : {}'.format(ret))

        if ret == []:
            err = 'No episodes found in url "{}"'.format(self.url)
            args = [self.url]
            raise NotFoundError(err, *args)

        ret = ret[::-1]
        return ret

    def _getMetadata(self, soup):
        info_div = soup.find('div', {'class': 'barContent'})
        self.title = info_div.find('a', {'class': 'bigChar'}).text
