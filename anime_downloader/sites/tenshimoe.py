from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import re


class TenshiMoe(Anime, sitename='tenshi.moe'):

    sitename = 'tenshi.moe'

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(
            helpers.get(
                'https://tenshi.moe/anime',
                params={'q': query},
                cookies={'loop-view': 'thumb'},
                cache=False
            )
        )

        results = soup.select('ul.thumb > li > a')

        return [
            SearchResult(
                title=x['title'],
                url=x['href'],
                poster=x.find('img')['src']
            )
            for x in results
        ]

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        eps = soup.select(
            'li[class*="episode"] > a'
        )
        eps = [x['href'] for x in eps]
        return eps

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url).text)
        self.title = soup.select_one('span.value > span[title="English"]').parent.text.strip()
        self.meta['year'] = int(re.findall(r"(\d{4})", soup.select_one('li.release-date .value').text)[0])
        self.meta['airing_status'] = soup.select_one('li.status > .value').text.strip()
        self.meta['total_eps'] = int(soup.select_one('.entry-episodes > h2 > span').text.strip())
        self.meta['desc'] = soup.select_one('.entry-description > .card-body').text.strip()
        self.meta['poster'] = soup.select_one('img.cover-image').get('src', '')
        self.meta['cover'] = ''


class TenshiMoeEpisode(AnimeEpisode, sitename='tenshi.moe'):
    QUALITIES = ['360p', '480p', '720p', '1080p']

    def _get_sources(self):
        soup = helpers.soupify(helpers.get(self.url))
        soup = soup.select_one('.embed-responsive > iframe')

        mp4moe = helpers.soupify(helpers.get(soup.get('src'), referer=self.url))
        mp4moe = mp4moe.select_one('video#player')
        qualities_ = [x.get("title") for x in mp4moe.select('source')]
        sources = [
            ('no_extractor', x.get('src'))
            for x in mp4moe.select('source')
        ]

        if self.quality in qualities_:
            return [sources[qualities_.index(self.quality)]]
