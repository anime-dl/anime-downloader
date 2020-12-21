from anime_downloader.sites.anime import Anime, SearchResult
from anime_downloader.sites.nineanime import NineAnimeEpisode
from anime_downloader.sites import helpers

import re
import json

class AnimeSuge(Anime, sitename="animesuge"):
    sitename = "animesuge"

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.get("https://animesuge.io/ajax/anime/search", params={"keyword": query}).json()['html'])

        search_results = [
            SearchResult(
                title=x.find("div").text,
                url="https://animesuge.io" + x.get('href')
            )
            for x in soup.select("a:not(.more)")
        ]

        return search_results

    def _scrape_episodes(self):
        ep_url = "https://animesuge.io/ajax/anime/servers"
        _id = re.search(r".*-(.*)", self.url).group(1)

        soup = helpers.soupify(helpers.get(ep_url, params={'id': _id}))

        return ['https://animesuge.io' + x.get('href') for x in soup.select('a:not(.more)')]

    def _scrape_metadata(self):
        self.title = helpers.soupify(helpers.get(self.url)).find("h1").text


class AnimeSugeEpisode(NineAnimeEpisode, sitename='animesuge'):
    def _get_sources(self):
        # Get id and ep no. from url, e.g: https://animesuge.io/anime/naruto-xx8z/ep-190 -> xx8z, 190
        _id, ep_no = re.search(r".*\/anime\/.*-(.*?)\/.*-(\d+)$", self.url).group(1, 2)

        # Get sources json from html, e.g:
        """
        <a class="active" data-base="190" data-name-normalized="190" data-sources='{"28":"8e663a9230406b753ba778dba15c723b3bf221b61fbdde6e8adae899adbad7ab","40":"565ff0ca78263f80a8f8a344e06085854f87e3449e321032425498b9d129dbf0","35":"c800a3ec0dfe68265d685792375169007b74c89aa13849869a16a3674d971f45"}' href="/anime/naruto-xx8z/ep-190">190</a>"""
        data_sources = json.loads(helpers.soupify(helpers.get("https://animesuge.io/ajax/anime/servers",
                                  params={"id": _id, "episode": ep_no})).select(f"a[data-base='{ep_no}']")[0].get("data-sources"))

        # Only includes supported
        # Unsupported ones {'28': 'openstream'}
        id_source_map = {'35': 'mp4upload', '40': 'streamtape'}

        sources_list = []
        for key in id_source_map:
            if key in data_sources.keys():
                _id = data_sources[key]

                for _ in range(3):
                    try:
                        link = helpers.get("https://animesuge.io/ajax/anime/episode",
                                           params={"id": _id}).json()['url']
                        break
                    # Makes it more consistent.
                    except HTTPError:
                        time.sleep(5)
                        continue

                server = id_source_map[key]
                sources_list.append({
                    'extractor': server,
                    'url': self.decodeString(link),
                    'server': server,
                    # This may not be true, can't see the info on page.
                    'version': 'subbed'
                })

        return self.sort_sources(sources_list)
