from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from anime_downloader.extractors import get_extractor
import json
import re


class AnimeFrenzy(Anime, sitename='animefrenzy'):
    sitename = 'animefrenzy'

    @classmethod
    def search(cls, query):
        r = helpers.get("https://old.animefrenzy.org/search", params={"term": query})
        soup = helpers.soupify(r)
        # Warning, assuming only these links!
        # Can cause errors in the future.
        results = soup.select('a[href^="https://old.animefrenzy.org/anime/"]')
        search_results = [
            SearchResult(
                title=results[i].text,
                url=results[i]['href']
            )
            # Skips the first result as it's "Random".
            for i in range(len(results)) if i and results[i].text.strip()
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
                sources = json.loads(re.search(r"\[.*host.*id.*?\]", str(i)).group())

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
