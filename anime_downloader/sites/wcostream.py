from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.extractors import get_extractor
from anime_downloader.sites import helpers

import re


class WcoStream(Anime, sitename='wcostream'):

    sitename = 'wcostream'

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.get(
            'https://wcostream.cc/search',
            params={'keyword': query}
        ))
        results = soup.select('.film_list-wrap > .flw-item')

        return [
            SearchResult(
                title=x.find('img')['alt'],
                url=x.find('a')['href'],
                meta={'year': x.select_one('.fd-infor > .fdi-item').text.strip()},
                meta_info={
                    'version_key_dubbed': '(Dub)'
                }
            )
            for x in results
        ]

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        episodes = soup.select_one('#content-episodes').select('ul.nav > li.nav-item')  # noqa
        return [
            x.find('a')['href']
            for x in episodes
            if 'javascript' not in str(x)
        ]

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.select_one(
            'meta[property="og:title"]'
        )['content'].split('Episode')[0].strip()


class WcoStreamEpisode(AnimeEpisode, sitename='wcostream'):
    def _get_sources(self):
        soup = helpers.soupify(helpers.get(self.url))
        servers = soup.select("#servers-list > ul > li")
        servers = [
            {
                "name": server.find('span').text.strip(),
                "link": server.find('a')['data-embed']
            }
            for server in servers
        ]

        servers = sorted(servers, key=lambda x: x['name'].lower() in self.config['servers'][0].lower())[::-1]  # noqa
        sources = []

        for server in servers:
            ext = get_extractor('wcostream')(
                server['link'],
                quality=self.quality,
                headers={}
            )
            sources.extend([('no_extractor', x['stream_url']) for x in ext._get_data()])  # noqa

        return sources
