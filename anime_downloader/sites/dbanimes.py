
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from urllib.parse import urlparse
from requests.exceptions import HTTPError
import logging
import re

logger = logging.getLogger(__name__)

class DBAnimes(Anime, sitename='dbanimes'):
    sitename = 'dbanimes'

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.get("https://dbanimes.com", params = {'s': query, 'post_type': 'anime'}))

        return [
            SearchResult(
                title = x['title'].strip(),
                url = x['href']
            )
            for x in soup.select('h6.fet > a')
        ]

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        return [x['href'] for x in soup.select('a.btn.btn-default.mb-2')]

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.select("li[aria-current=page]")[0].text

class DBAnimesEpisode(AnimeEpisode, sitename='dbanimes'):
    def check_server(self, extractor, url):
        #Sendvid returns 404
        try:
            soup = helpers.soupify(helpers.get(url))
        except HTTPError:
            return False

        if extractor == 'mixdrop':
            try:
                return soup.h2.text != "WE ARE SORRY"
            except AttributeError:
                return True
        if extractor == "fembed":
            try:
                return soup.p.text != 'Sorry this video does not exist'
            except AttributeError:
                return True

    def _get_sources(self):
        soup = helpers.soupify(helpers.get(self.url))
        servers = [re.sub('^//', 'https://', helpers.soupify(x['data-url']).iframe['src']) for x in soup.select('li.streamer > div[data-url]')]
        server = self.config['server']
        fallbacks = self.config['fallback_servers']
        domains = [re.search("(.*)\.", urlparse(x).netloc).group(1).replace('www.', '') for x in servers]

        if server in domains:
            extractor = server if server != 'fembed' else 'gcloud'
            link = servers[domains.index(server)]

            #Just In Case
            exists = self.check_server(extractor, link)
            if exists:
                return [(extractor, link)]

        available = list(set(fallbacks) & set(domains))

        for fallback in fallbacks:
            if fallback in available:
                extractor = fallback if fallback != 'fembed' else 'gcloud'
                matches = [i for i, x in enumerate(domains) if x == fallback]

                if matches:
                    for match in matches:
                        link = servers[match]
                        exists = self.check_server(extractor, link)

                        if exists:
                            return [(extractor, link)]

        logger.warn("No supported servers found")
        return
