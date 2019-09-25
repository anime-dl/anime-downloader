from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

class Itsaturday(Anime, sitename='itsaturday'):
    sitename = 'itsaturday'
    DOMAIN = 'http://www.itsaturday.com'

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.get(f"{cls.DOMAIN}/search/", params={'q': query}))
        results = [
            SearchResult(title=t.text, url=cls.DOMAIN + t.attrs['href'], poster=t.img.attrs.get('data-src', None))
            for t in soup.select('.preview > a')
        ]
        return results

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        ret = [
            (t.text, self.DOMAIN + t.attrs['href'])
            for t in soup.select('a.link-group-item')
        ]
        return ret

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.select_one('h1.h3').text


class ItsaturdayEpisode(AnimeEpisode, sitename='itsaturday'):
    def _get_sources(self):
        return [
            ('no_extractor',
             self._parent.DOMAIN + helpers.soupify(helpers.get(self.url)).select_one('source').attrs['src'])
        ]

