import re

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

class Nyaa(Anime, sitename = 'nyaa'):
    """
    Site: https://nyaa.si

    Config
    ~~~~~~
    filter: Choose filter method in search. One of ['No filter', 'No remakes', 'Trusted Only']
    category: Choose categories to search. One of ['Anime Music Video', 'English-translated', 'Non-English-translated']
    """

    sitename = 'nyaa'
    url = f'https://{sitename}.si'

    @classmethod
    def search(cls, query):
        filters = {"No filter": 0, "No remakes": 1, "Trusted only": 2}
        categories = {"Anime Music Video": "1_1", "English-translated": "1_2", "Non-English-translated": "1_3"}

        rex = r'(magnet:)+[^"]*'
        self = cls()

        parameters = {"f": filters[self.config["filter"]], "c": categories[self.config["category"]], "q": query, "s": "size", "o": "desc"}
        search_results = helpers.soupify(helpers.get(f"https://nyaa.si/", params = parameters))

        search_results = [
            SearchResult(
                title = i.select("a:not(.comments)")[1].get("title"),
                url = i.find_all('a',{'href':re.compile(rex)})[0].get('href'),
                meta= {'peers':i.find_all('td',class_ = 'text-center')[3].text + ' peers','size':i.find_all('td',class_ = 'text-center')[1].text})

            for i in search_results.select("tr.default, tr.success")
            ]

        return search_results
        
    def _scrape_episodes(self):
        #the magnet has all episodes making this redundant
        return [self.url]

class NyaaEpisode(AnimeEpisode, sitename='nyaa'):
    def _get_sources(self):
        return [('no_extractor', self.url)]
