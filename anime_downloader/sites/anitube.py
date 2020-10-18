from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import re


class AniTube(Anime, sitename="anitube"):
    sitename = "anitube"

    @classmethod
    def search(cls, query):
        base_url = 'https://www.anitube.site'
        html = helpers.soupify(helpers.get(base_url, params={'s': query}))
        results = html.select('div.aniItem > a')

        return [
            SearchResult(
                title=x['title'].split(
                    'Temporada')[0].split('– Todos')[0].split(
                    'Todos os')[0],
                url=x['href'],
                meta_info={'version_key_dubbed': '(Dublado)'}
            )
            for x in html.select('div.aniItem > a')
        ]
        return results

    def _scrape_episodes(self):
        html = helpers.soupify(helpers.get(self.url))
        eps = html.select('div.pagAniListaContainer.targetClose > a')
        return [x['href'] for x in eps]

    def _scrape_metadata(self):
        html = helpers.soupify(helpers.get(self.url))
        title = html.select_one('div.mwidth > h1').text
        title = title.split('– Todos')[0]
        title = title.split('Todos os')[0]
        self.title = title.strip()


class AniTubeEpisode(AnimeEpisode, sitename='anitube'):
    def _get_sources(self):
        html = helpers.soupify(helpers.get(self.url))
        scripts = html.find_all('script', type="text/javascript")

        for script in scripts:
            if 'var play' in str(script):
                js = script

        link = re.search(r"file.*?[\"'](http.*?)['\"]", str(js)).group(1)
        return [('no_extractor', link)]
