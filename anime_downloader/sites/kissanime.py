import re
import logging

from anime_downloader.sites.anime import AnimeEpisode, SearchResult, Anime
from anime_downloader.sites import helpers
from anime_downloader.sites.exceptions import NotFoundError

logger = logging.getLogger(__name__)


class KissanimeEpisode(AnimeEpisode, sitename='kissanime'):
    QUALITIES = ['360p', '480p', '720p', '1080p']
    _base_url = 'http://kissanime.ru'
    VERIFY_HUMAN = True

    def _get_sources(self):
        ret = helpers.get(self.url+'&s=rapidvideo', cf=True)
        data = self._scrape_episode(ret)
        return data

    def _scrape_episode(self, response):
        rapid_re = re.compile(r'iframe.*src="https://(.*?)"')
        rapid_url = rapid_re.findall(response.text)[0]
        return [('rapidvideo', rapid_url)]


class KissAnime(Anime, sitename='kissanime'):
    sitename = 'kissanime'
    _referer = 'http://kissanime.ru'
    QUALITIES = ['360p', '480p', '720p', '1080p']

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.post(
            'https://kissanime.ru/Search/Anime',
            data=dict(keyword=query),
            referer=cls._referer,
            cf=True
        ))

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
            logger.debug(res)
            ret.append(res)

        return ret

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url, cf=True))
        ret = ['http://kissanime.ru'+str(a['href'])
               for a in soup.select('table.listing a')]
        logger.debug('Unfiltered episodes : {}'.format(ret))
        filter_list = ['opening', 'ending', 'special', 'recap']
        ret = list(filter(
            lambda x: not any(s in x.lower() for s in filter_list), ret
        ))
        logger.debug('Filtered episodes : {}'.format(ret))

        if ret == []:
            err = 'No episodes found in url "{}"'.format(self.url)
            args = [self.url]
            raise NotFoundError(err, *args)

        ret = ret[::-1]
        return ret

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url, cf=True))
        info_div = soup.select_one('.barContent')
        self.title = info_div.select_one('a.bigChar').text
