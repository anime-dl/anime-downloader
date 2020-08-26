import logging
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from anime_downloader.const import HEADERS

logger = logging.getLogger(__name__)

class Anime4(Anime, sitename = '4anime'):
    sitename = '4anime'

    @classmethod
    def search(cls, query):
        data = {
            "action": "ajaxsearchlite_search", 
            "aslp": query, 
            "asid": 1, 
            "options": "qtranslate_lang=0&set_intitle=None&customset%5B%5D=anime"
            }
        soup = helpers.soupify(helpers.post("https://4anime.to/wp-admin/admin-ajax.php", data=data)).select('div.info > a')

        search_results = [
            SearchResult(
                title = i.text,
                url = i['href']
                )
            for i in soup
            ]
        return search_results

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url)).select('ul.episodes.range.active > li > a')
        return [x['href'] for x in soup]


    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url).text)
        self.title = soup.title.text
        for i in soup.select('.detail > a'):
            if 'year' in i.get('href',''):
                self.meta['year'] = int(i.text) if i.text.isnumeric() else None


class Anime4Episode(AnimeEpisode, sitename='4anime'):
    def _get_sources(self):
        self.headers = {'user-agent':HEADERS[self.hash_url(self.url, len(HEADERS))]}
        resp = helpers.get(self.url, headers=self.headers)
        stream_url = helpers.soupify(resp).find('div', class_='videojs-desktop').find('source')['src']
        return [('no_extractor', stream_url)]


    """
    Let's say the user generates link A with user agent X.
    Upon retry of command it'd normally use Link A (cached), but with user agent Y
    which would error because the user agent isn't consistent.

    This 'hashes' the url to generate a 'random' header which is consistent throughout multiple commands.
    """
    def hash_url(self, url, length):
        total = 0
        for i in url:
            total += ord(i)
        return total%length
