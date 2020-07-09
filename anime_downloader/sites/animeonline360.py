import json, requests

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

class AnimeOnline(Anime, sitename = 'animeonline360'):

    sitename = 'animeonline360'
    url = f'https://{sitename}.me'

    @classmethod
    def search(cls, query):
        try:
            # r = helpers.get('https://animeonline360.me/wp-json/dooplay/search/?nonce=12d75e884b', params = {'keyword': query}).json()
            r = helpers.soupify(helpers.get('https://animeonline360.me/', params = {'s': query})).select('div.title')
            results = [{"title": x.text, "url": x.a['href']} for x in r]
            search_results = [
                SearchResult(
                    title = i['title'],
                    url = i['url'],
                    meta= {})

                for i in results
                ]

            return search_results
        except:
            return ""

    def _scrape_episodes(self):

        r = helpers.get(self.url).text
        soup = helpers.soupify(r)
        try:
            soup = soup.find('div', id="seasons").find_all('li')
            episodes = []
            for i in soup:
                data = i.find('div', class_='episodiotitle')
                url = data.a['href']
                episode = int(i.find('div', class_='numerando').text.replace('Episode ', ''))
                title = data.a.text
                entry = {"title": title, "episode": episode, "url": url}
                episodes.append(entry)
            episodes.reverse()
            return [x['url'] for x in episodes]
        except:
            return [self.url]

    def _scrape_metadata(self):
            self.title = helpers.soupify(helpers.get(self.url)).title.text.split('|')[0].strip().title()


class AnimeOnline360Episode(AnimeEpisode, sitename='animeonline360'):
    def _get_sources(self):
        return [('animeonline360', self.url)]
