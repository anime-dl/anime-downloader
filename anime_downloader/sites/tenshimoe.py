import json
import os
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

class TenshiMoe(Anime, sitename = 'tenshi.moe'):

    sitename = 'tenshi.moe'

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.get('https://tenshi.moe/anime', params={'q': query}).text)
        soup = soup.find('ul', class_="loop anime-loop list")
        results = soup.select('li')

        return [
            SearchResult(
                title=x.a['title'],
                url=x.a['href'],
                )
            for x in results
            ]

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url).text).find_all('ul', class_="loop episode-loop list")
        eps = [x.a['href'] for x in soup]
        return eps

    def _scrape_metadata(self):
            soup = helpers.soupify(helpers.get(self.url).text)
            self.title = soup.title.text.split('—')[0].strip()
            
class TenshiMoeEpisode(AnimeEpisode, sitename='tenshi.moe'):
    def _get_sources(self):
        soup = helpers.soupify(helpers.get(self.url).text)
        link = soup.find_all('source', type="video/mp4")[-1]['src']
        return [('no_extractor', link)]
