from anime_downloader.sites import helpers
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult

class KissAnimeX(Anime, sitename = 'kissanimex'):
    sitename = "kissanimex"

    @classmethod
    def search(cls, query):
        url = 'https://kissanimex.com/search?url=search'
        r = helpers.get(url, params={'q': query})
        soup = helpers.soupify(r.text)
        items = soup.select('td > a')
        search_results = [
                SearchResult(
                    title = x.find('a').text,
                    url = 'https://kissanimex.com' + x.find('a')['href']
                    )
                for x in items
                ]
        return search_results

    def _scrape_episodes(self):
        r = helpers.get(self.url).text
        eps = helpers.soupify(r).find('div', id='episodes-sub').select('td > a')
        episodes = ['https://kissanimex.com' + x.get('href') for x in eps][::-1]
        return episodes

    def _scrape_metadata(self):
        self.title = helpers.soupify(helpers.get(self.url).text).find('a', class_='bigChar').text

class KissAnimeXEpisode(AnimeEpisode, sitename='kissanimex'):
    def _get_sources(self):
        r = helpers.get(self.url).text
        soup = helpers.soupify(r).find('div', class_='host', id='menu')
        sources = soup.find_all('a')
        sources = [x['data-video-link'] for x in sources]
        #TODO make this source rotate because there may be other sources
        for a in sources:
            if 'vidstreaming' in a:
                source = a
        return [('vidstream', a)]
