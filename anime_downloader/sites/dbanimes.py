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
            soup = helpers.soupify(helpers.get(url,allow_redirects=True))
        except HTTPError:
            return False

        if extractor == 'mixdrop':
            # Checks redirects in mixdrop.
            redirect_regex = r"\s*window\.location\s*=\s*('|\")(.*?)('|\")"
            redirect = re.search(redirect_regex,str(soup))
            if redirect:
                url = 'https://mixdrop.to' + redirect.group(2)
                soup = helpers.soupify(helpers.get(url))

            try:
                return soup.h2.text != "WE ARE SORRY"
            except AttributeError:
                return True

        if extractor == "gcloud":
            try:
                return soup.p.text != 'Sorry this video does not exist'
            except AttributeError:
                return True

        if extractor == "mp4upload":
            return 'File was deleted' not in soup

        # Default extractor always returns true
        return True

    def _get_sources(self):
        soup = helpers.soupify(helpers.get(self.url))
        sources = [re.sub('^//', 'https://', helpers.soupify(x['data-url']).iframe['src']) for x in soup.select('li.streamer > div[data-url]')]
        domains = [re.search("(.*)\.", urlparse(x).netloc).group(1).replace('www.', '') for x in sources]

        servers = self.config['servers']

        logger.debug('Sources: {}'.format(sources))
        logger.debug('Domains: {}'.format(domains))

        # Exceptions to domain -> extractor
        extractor_dict = {
            'fembed':'gcloud',
            'gounlimited':'mp4upload'
        }

        sources_list = []
        for i in range(len(sources)):
            if domains[i] in servers:
                extractor = extractor_dict.get(domains[i],domains[i])
                if self.check_server(extractor, sources[i]):
                    sources_list.append({
                    'extractor':extractor,
                    'url':sources[i],
                    'server':domains[i],
                    'version':'subbed'
                    })

        return self.sort_sources(sources_list)
