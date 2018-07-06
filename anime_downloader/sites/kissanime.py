import cfscrape
from bs4 import BeautifulSoup
import re
import logging

from anime_downloader.sites.anime import BaseEpisode, SearchResult
from anime_downloader.sites.baseanimecf import BaseAnimeCF
from anime_downloader.sites.exceptions import NotFoundError
from anime_downloader.const import get_random_header


scraper = cfscrape.create_scraper(delay=10)


class KissanimeEpisode(BaseEpisode):
    QUALITIES = ['360p', '480p', '720p']
    _base_url = 'http://kissanime.ru'
    VERIFY_HUMAN = True

    def _get_sources(self):
        episode_url = self.url+'&s=rapidvideo'
        logging.debug('Calling url: {}'.format(episode_url))

        ret = scraper.get(episode_url)
        data = self._scrape_episode(ret)

        return data

    def _scrape_episode(self, response):
        rapid_re = re.compile(r'iframe.*src="https://(.*?)"')
        rapid_url = rapid_re.findall(response.text)[0]

        return [('rapidvideo', rapid_url)]


class KissAnime(BaseAnimeCF):
    sitename = 'kissanime'
    _referer = 'http://kissanime.ru/'
    QUALITIES = ['360p', '480p', '720p']
    _episodeClass = KissanimeEpisode

    @classmethod
    def search(cls, query):
        headers = get_random_header()
        headers['referer'] = 'http://kissanime.ru/'
        res = scraper.post(
            'http://kissanime.ru/Search/Anime',
            data={
                'type': 'Anime',
                'keyword': query,
            },
            headers=headers,
        )

        soup = BeautifulSoup(res.text, 'html.parser')

        # If only one anime found, kissanime redirects to anime page.
        # We don't want that
        if soup.title.text.strip().lower() != "find anime":
            return [SearchResult(
                title=soup.find('a', 'bigChar').text,
                url='https://kissanime.ru' +
                    soup.find('a', 'bigChar').get('href'),
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

    def _scarpe_episodes(self, soup):
        ret = soup.find('table', {'class': 'listing'}).find_all('a')
        ret = ['http://kissanime.ru'+str(a['href']) for a in ret]
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

    def _scrape_metadata(self, soup):
        info_div = soup.find('div', {'class': 'barContent'})
        self.title = info_div.find('a', {'class': 'bigChar'}).text
