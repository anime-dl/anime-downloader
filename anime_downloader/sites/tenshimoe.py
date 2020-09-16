from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers


class TenshiMoe(Anime, sitename='tenshi.moe'):

    sitename = 'tenshi.moe'

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(
            helpers.get('https://tenshi.moe/anime', params={'q': query}))
        results = soup.select('ul.loop.anime-loop.list > li > a')

        return [
            SearchResult(
                title=x['title'],
                url=x['href'],
            )
            for x in results
        ]

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        eps = soup.select(
            'li[class^=episode] > a'
        )
        eps = [x['href'] for x in eps]
        return eps

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url).text)
        self.title = soup.title.text.split('—')[0].strip()


class TenshiMoeEpisode(AnimeEpisode, sitename='tenshi.moe'):
    def _get_sources(self):
        soup = helpers.soupify(helpers.get(self.url))
        # Might break with something other than mp4!
        link = soup.find_all('source', type="video/mp4")[-1]['src']
        return [('no_extractor', link)]
