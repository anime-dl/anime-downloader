
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import re
import logging

logger = logging.getLogger(__name__)

class VostFree(Anime, sitename='vostfree'):
    """
    Site: https://vostfree.com
    Config
    ------
    server: One of ['sibnet', 'uqload']
    """

    sitename = 'vostfree'

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.post('https://vostfree.com', data = {'do': 'search', 'subaction': 'search', 'story': query}))
        return [
            SearchResult(
                title = re.sub('\s+?FRENCH(\s+)?$', '', x.text.strip()),
                url = x['href']
            )
            for x in soup.select('div.title > a')
        ]

    def getLink(self, _id, server):
        if server == 'sibnet':
            return f'https://video.sibnet.ru/shell.php?videoid={_id}'
        elif server == 'uqload':
            return f'https://uqload.com/embed-{_id}.html'

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        server = self.config['server']
        servers = ['sibnet', 'uqload']
        players = soup.select('div[id*=buttons]')
        links = []

        for player in players:
            current = player.select(f'div.new_player_{server}')
            if current:
                links.append(self.getLink(soup.find('div', {'id': f'content_{current[0]["id"]}'}).text, server))
                continue

            alternate_server = servers[int(not bool(servers.index(server)))]
            current = player.select(f'div.new_player_{alternate_server}')

            if current:
                links.append(self.getLink(soup.find('div', {'id': f'content_{current[0]["id"]}'}).text, alternate_server))
                continue
            

        return links

    def _scrape_metadata(self):
       soup = helpers.soupify(helpers.get(self.url))
       self.title = re.sub('\s+?FRENCH(\s+)?$', '', soup.select('meta[property=og\:title]')[0]['content'])

class VostFreeEpisode(AnimeEpisode, sitename='vostfree'):
    def _get_sources(self):
        extractor = "sibnet" if "sibnet" in self.url else "uqload"
        return [(extractor, self.url)]
