import json, re

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

class DarkAnime(Anime, sitename = 'darkanime'):

    sitename = 'darkanime'

    @classmethod
    def search(cls, query):

        soup = helpers.soupify(helpers.get('https://app.darkanime.stream/api/v1/animes', params={'term': query}).json()['animesHtml'])
        soup = soup.find_all('a', href=True)
        results = [[x.find('h3').text.strip(), 'https://app.darkanime.stream' + x['href']] for x in soup]
        search_results = [
            SearchResult(
                title = i[0],
                url = i[1],
                )
            for i in results
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
    def _get_sources(self):
        soup = helpers.soupify(helpers.get(self.url).text)
        players = soup.find_all('iframe')
        sources = soup.find_all('script')[-3].string
        regex = r"\[([^)]+)\]"
        sources = json.loads('[' + re.search(regex, sources).group(1) + ']')
        link = 'https://www.mp4upload.com/embed-{}.html'.format(sources[-1]['source']) if sources[-1]['host'] == 'mp4upload' else 'https://www.mp4upload.com/embed-{}.html'.format(sources[0]['source'])
        return [('mp4upload', link)]