import logging
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

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
        soup = helpers.soupify(helpers.post("https://4anime.to/wp-admin/admin-ajax.php", data=data).text)

        search_results = [
            SearchResult(
                title = i.find('div', class_='info').a.text,
                url = i.find('div', class_='info').a['href']
                )
            for i in soup.find_all('div', class_='item')
            ]
        return search_results

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url).text).find('ul', class_='episodes range active').find_all('li')
        return [x.a['href'] for x in soup]

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url).text)
        self.title = soup.title.text
        for i in soup.select('.detail > a'):
            if 'year' in i.get('href',''):
                self.meta['year'] = int(i.text) if i.text.isnumeric() else None

class Anime4Episode(AnimeEpisode, sitename='4anime'):
    def _get_sources(self):
        stream_url = helpers.soupify(helpers.get(self.url).text).find('div', class_='videojs-desktop').find('source')['src']
        return [('no_extractor', stream_url)]
