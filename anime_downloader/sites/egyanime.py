import logging
import re
import urllib.parse
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)


class EgyAnime(Anime, sitename='egyanime'):
    sitename = 'egyanime'

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.get('https://www.egyanime.com/a.php', params={'term': query}).text)

        search_results = [
            SearchResult(
                title = i.text,
                url= "https://www.egyanime.com/" + i['href']
                )
            for i in soup.find_all('a', href=True)
        ]
        return search_results

    def _scrape_episodes(self):
        """
        Because of how the website is built, 
        the only way to access the episodes is by going to the last episode available
        thats why im making two requests here.
        """
        soup = helpers.soupify(helpers.get(self.url).text)
        eps = ["https://www.egyanime.com/" + x['href'] for x in soup.select('a.tag.is-dark.is-medium.m-5')]
        return eps

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url).text)
        self.title = soup.title.text.split('مشاهدة')[0].strip()


class EgyAnimeEpisode(AnimeEpisode, sitename='egyanime'):
    def _get_sources(self):
        soup = helpers.soupify(helpers.get(self.url).text)
        servers = [x['data-link'] for x in soup.select('div.server-watch#server-watch > a')]
        logger.debug('Hosts: ' + str([urllib.parse.urlparse(x).netloc for x in servers]))
        sources = []
        for i in servers:
            if 'clipwatching' in i:
                sources.append({
                    'extractor': 'clipwatching',
                    'url': i,
                    'server': 'clipwatching',
                    'version': '1'
                })
            elif 'streamtape' in i:
                sources.append({
                    'extractor': 'streamtape',
                    'url': i,
                    'server': 'streamtape',
                    'version': '1'
                })
        return self.sort_sources(sources)
