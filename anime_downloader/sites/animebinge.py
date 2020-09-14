import logging
import json
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from anime_downloader.extractors import get_extractor

logger = logging.getLogger(__name__)


class AnimeBinge(Anime, sitename='animebinge'):
    sitename = 'animebinge'

    @classmethod
    def search(cls, query):
        response = helpers.get('https://animebinge.net/search', params={'term': query}).text
        soup = helpers.soupify(response)
        results = soup.select('a#epilink')

        search_results = [
            SearchResult(
                title=x.text,
                url=x['href']
                )
            for x in results
            ]
        return search_results

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url).text).select_one('div.anime#sub')
        eps = soup.select('div.episode-wrap')
        eps = [x.a['href'] for x in eps]
        eps.reverse()
        return eps

    def _scrape_metadata(self):
        self.title = helpers.soupify(helpers.get(self.url).text).select_one('div.contingo > p').text

class AnimeBingeEpisode(AnimeEpisode, sitename='animebinge'):
    def _get_sources(self):
        soup = helpers.soupify(helpers.get(self.url).text)
        sources = soup.find_all('script')

        for source in sources:
            if 'var episode' in str(source):
                sources = json.loads(str(source).split('var episode = ')[1].replace(';\n', '').replace('</script>', '').strip())['videos']
                break

        logger.debug('Sources: {}'.format(sources))

        mappings = {
            'mp4upload': 'https://www.mp4upload.com/embed-{}.html',
            'trollvid': 'https://trollvid.net/embed/{}'
        }

        sources_list = []
        for i in sources:        
            extractor = 'no_extractor' if not get_extractor(i['host']) else i['host']
            sources_list.append({
            'extractor':extractor,
            'url': mappings.get(i['host'], None).format(i['id']),
            'server':i['host'],
            'version':i.get('type','subbed')
            })

        return self.sort_sources(sources_list)