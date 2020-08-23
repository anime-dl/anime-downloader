from anime_downloader.sites import helpers
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
import logging

logger = logging.getLogger(__name__)

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
                    title = x.text,
                    url = 'https://kissanimex.com' + x['href']
                    )
                for x in items
                ]
        return search_results

    def _scrape_episodes(self):
        r = helpers.get(self.url).text
        soup = helpers.soupify(r)
        if self.config['version'] == 'dubbed':
            try:
                eps = soup.select_one('div#episodes-dub').select('td > a')
                if len(eps) == 0:
                    raise Exception
            except:
                logger.info('You have dubbed in the config, but this anime doesnt have a dub.')
                return []
        else:
            eps = soup.select_one('div#episodes-sub').select('td > a')
        episodes = ['https://kissanimex.com' + x.get('href') for x in eps][::-1]
        return episodes

    def _scrape_metadata(self):
        self.title = helpers.soupify(helpers.get(self.url).text).select_one('a.bigChar').text

class KissAnimeXEpisode(AnimeEpisode, sitename='kissanimex'):
    def _get_sources(self):
        r = helpers.get(self.url).text
        soup = helpers.soupify(r).find('div', class_='host', id='menu')
        sources = soup.find_all('a')
        sources = [x['data-video-link'] for x in sources]
        
        
        map_2_dict = {
            'vidstream': 'vidstream'
        }
        for a in sources:
            for i in map_2_dict:
                if i in a:
                    return [(i, a)]
