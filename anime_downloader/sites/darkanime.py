import json
import re

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

class DarkAnime(Anime, sitename = 'darkanime'):
    sitename = 'darkanime'

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.get('https://app.darkanime.stream/api/v1/animes', params={'term': query}).json()['animesHtml'])
        soup = soup.find_all('a', href=True)
        search_results = [
            SearchResult(
                title = x.find('h3').text.strip(),
                url = 'https://app.darkanime.stream' + x['href'],
                )
            for x in soup
            ]
        return search_results
    
    def _scrape_episodes(self):
        html = helpers.soupify(helpers.get(self.url).text)
        eps = html.find('ul', class_='mt-4').find_all('li')
        eps = ['https://app.darkanime.stream' + x.a['href'] for x in eps]
        eps.reverse()
        return eps
    
    def _scrape_metadata(self):
            self.title = helpers.soupify(helpers.get(self.url).text).find_all('h2')[0].text.strip()
            
class DarkAnimeEpisode(AnimeEpisode, sitename='darkanime'):
    def getLink(self, name, _id):
        if name == "trollvid":
            return "https://trollvid.net/embed/" + _id
        elif name == "mp4upload":
            return f"https://mp4upload.com/embed-{_id}.html"
        elif name == "xstreamcdn":
            return "https://www.xstreamcdn.com/v/" + _id

    def _get_sources(self):
        server = self.config.get("server", "mp4upload")
        resp = helpers.soupify(helpers.get(self.url).text).find_all('script')[-3].string
        hosts = json.loads(re.search(r"(\[[^)]+\])", resp).group(1))
        _type = hosts[0]["type"]
        try:
            host = list(filter(lambda video: video["host"] == server and video["type"] == _type, hosts))[0]
        except IndexError:
            host = hosts[0]
            if host["host"] == "mp4upload" and len(hosts) > 1:
                host = hosts[1]

        name = host["host"]
        _id = host["source"]
        link = self.getLink(name, _id)

        return [(name, link)]
