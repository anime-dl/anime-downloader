from anime_downloader.sites import helpers
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult

class AnimeChameleon(Anime, sitename = 'gurminder'):
    sitename = "gurminder"
    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.get('http://anime.gurminderboparai.com/search/{}'.format(query)).text).find('div', class_='panel-body').find_all('a')
        search_results = [
            SearchResult(
                title = x.text,
                url = x['href']
                )
            for x in soup
            ]
        return search_results

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url).text).find('ul', id='episodes-list').find_all('li')
        eps = [x.a['href'] for x in soup]
        eps.reverse()
        return eps

    def _scrape_metadata(self):
        self.title = helpers.soupify(helpers.get(self.url).text).find('h3', class_='panel-title').text

class AnimeChameleonEpisode(AnimeEpisode, sitename='gurminder'):
    def _get_sources(self):
        url = helpers.soupify(helpers.get(self.url).text).find('iframe', id='video')['src'].replace('//', 'http://')
        return [('trollvid', url)]
