from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from anime_downloader.extractors import get_extractor
import json
import re


class AnimeFrenzy(Anime, sitename='animefrenzy'):
    sitename = 'animefrenzy'

    @classmethod
    def search(cls, query):
        r = helpers.get("https://old.animefrenzy.org/search", params = {"term": query})
        soup = helpers.soupify(r)
        results = soup.find_all("a", href=lambda x: x and 'https://old.animefrenzy.org/anime/' in x)
        filter_out_results = {}

        for i in results:
            filter_out_results[i['href']] = i.text
        del filter_out_results[results[0]['href']]

        search_results = [
            SearchResult(
                title=value,
                url=key
            )
            for key, value in filter_out_results.items()
        ]
        return search_results

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        eps = [x['href'] for x in soup.select('div.ani-epi > a')]

        return eps[::-1]

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.title.text.split('- Watch Anime')[0].strip()


class AnimeFrenzyEpisode(AnimeEpisode, sitename='animefrenzy'):
    def _get_sources(self):

        mappings = {
            'mp4upload': 'https://www.mp4upload.com/embed-{}.html',
            'trollvid': 'https://trollvid.net/embed/{}',
            'xstreamcdn': 'https://xstreamcdn.com/v/{}'
        }

        soup = helpers.soupify(helpers.get(self.url))
        scripts = soup.select('script')

        for i in scripts:

            if 'var episode_videos' in str(i):
                sources = json.loads(re.search("\[.*host.*id.*?\]", str(i)).group())

        sources_list = []
        for i in sources:
            if mappings.get(i.get('host')):
                extractor = 'no_extractor' if not get_extractor(i['host']) else i['host']
                sources_list.append({
                    'extractor': extractor,
                    'url': mappings[i['host']].format(i['id']),
                    'server': i['host'],
                    'version': i.get('type', 'subbed')
                })

        return self.sort_sources(sources_list)
