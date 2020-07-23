import logging
import json
import re

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)

class DarkAnime(Anime, sitename = 'darkanime'):
    sitename = 'darkanime'

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.get('https://app.darkanime.stream/api/v1/animes', params={'term': query}).json()['animesHtml'])
        soup = soup.find_all('a', href=True)
        return [
            SearchResult(
                title = x.find('h3').text.strip(),
                url = 'https://app.darkanime.stream' + x['href'],
                )
            for x in soup
            ]


    def _scrape_episodes(self):
        html = helpers.soupify(helpers.get(self.url).text)
        eps = html.find('ul', class_='mt-4').find_all('li')
        eps = ['https://app.darkanime.stream' + x.a['href'] for x in eps]
        eps.reverse()
        return eps


    def _scrape_metadata(self):
        self.title = helpers.soupify(helpers.get(self.url).text).find_all('h2')[0].text.strip()


class DarkAnimeEpisode(AnimeEpisode, sitename='darkanime'):
    def _get_sources(self):

        server_links = {
            'mp4upload':'https://www.mp4upload.com/embed-{}.html',
            'trollvid': 'https://trollvid.net/embed/{}',
        }

        resp = helpers.soupify(helpers.get(self.url).text).find_all('script')#[-3].string
        for i in resp:
            if i.string:
                if 'sources' in i.string:
                    res = i.string

        hosts = json.loads(re.search(r"(\[[^)]+\])", res).group(1))
        logger.debug('Hosts: {}'.format(hosts))

        sources_list = []
        for i in hosts:
            for j in server_links:
                if i.get('host') in j and i.get('source'):
                    sources_list.append({
                        'extractor':j,
                        'url':server_links[j].format(i['source']),
                        'server':j,
                        'version':i['source']
                        })

        return self.sort_sources(sources_list)
