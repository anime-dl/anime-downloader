import re
import logging

from anime_downloader.sites.anime import AnimeEpisode, SearchResult, Anime
from anime_downloader.sites import helpers
from anime_downloader.sites.exceptions import NotFoundError

logger = logging.getLogger(__name__)


class KissanimeEpisode(AnimeEpisode, sitename='kissanime'):
    """KissanimeEpisode"""
    _base_url = 'https://kissanime.ru'

    def _get_sources(self):
        ret = helpers.get(self.url+'&s=hydrax', sel=True).text
        data = self._scrape_episode(ret)
        return data


    def _scrape_episode(self, response):
        regex = r'iframe.*src="(https://.*?)"'
        url = (re.search(regex,response).group(1))
        return [('hydrax', url)]


class KissAnime(Anime, sitename='kissanime'):
    """KissAnime"""
    sitename = 'kissanime'
    domain = 'https://kissanime.ru'
    _referer = 'https://kissanime.ru'
    QUALITIES = ['360p', '480p', '720p', '1080p']

    @classmethod
    def search(cls, query):
        sel = helpers.get("https://kissanime.ru",sel=True)
        cookies = sel.cookies
        agent = sel.user_agent # Note that the user agent must be the same as the one which generated the cookies
        cookies = {c['name']: c['value'] for c in cookies}
        soup = helpers.soupify((helpers.post("https://kissanime.ru/Search/Anime", headers = {
            "User-Agent": agent,
            "Referer": "https://kissanime.ru/Search/Anime"
            },data = {"keyword": query},cookies=cookies)))

        # If only one anime found, kissanime redirects to anime page.
        # We don't want that
        if soup.title.text.strip().lower() != "find anime":
            return [SearchResult(
                title=soup.find('a', 'bigChar').text,
                url=cls.domain +
                    soup.find('a', 'bigChar').get('href'),
                poster='',
            )]

        searched = [s for i, s in enumerate(soup.find_all('td')) if not i % 2]

        ret = []
        for res in searched:
            res = SearchResult(
                title=res.text.strip(),
                url=cls.domain + res.find('a').get('href'),
                poster='',
            )
            logger.debug(res)
            ret.append(res)

        return ret


    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url, sel=True).text)
        ret = [self.domain + str(a['href'])
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
        soup = helpers.soupify(helpers.get(self.url, sel=True).text)
        info_div = soup.select_one('.barContent')
        self.title = info_div.select_one('a.bigChar').text
