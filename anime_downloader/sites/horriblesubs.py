
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import re
import logging

logger = logging.getLogger(__name__)

class HorribleSubs(Anime, sitename='horriblesubs'):
    sitename = 'horriblesubs'

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.get("https://horriblesubs.info/api.php", params = {"method": "search", "value": query}))
        titlesDict = dict([(re.search('(.*)-', x.find(text = True, recursive = False)).group(1).strip(), x['href']) for x in soup.select('li > a')])

        return [
            SearchResult(
                title = x[0],
                url = 'https://horriblesubs.info' + x[1]
            )
            for x in titlesDict.items()
        ]

    def _scrape_episodes(self):
        show_id = re.search("var\shs_showid\s=\s(.*?);", helpers.get(self.url).text).group(1)

        next_id = 1
        episodes = []

        while True:
            resp = helpers.get('https://horriblesubs.info/api.php', params = {'method': 'getshows', 'type': 'show', 'showid': show_id, 'nextid': next_id})

            if resp.text == "DONE":
                if next_id == 1:
                    resp = helpers.get('https://horriblesubs.info/api.php', params = {'method': 'getshows', 'type': 'show', 'showid': show_id})
                else:
                    break

            soup = helpers.soupify(resp)
            episodes.extend([x['href'] for x in soup.select(f'div.rls-info-container .link-{self.quality} .hs-magnet-link > a')])
            next_id += 1

        return episodes[::-1]

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.h1.text

class HorribleSubsEpisode(AnimeEpisode, sitename='horriblesubs'):
    def _get_sources(self):
        return [('no_extractor', self.url)]
