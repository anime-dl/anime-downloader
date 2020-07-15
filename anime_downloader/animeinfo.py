from anime_downloader.sites import helpers
import logging
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from fuzzywuzzy import fuzz

logger = logging.getLogger(__name__)

class AnimeInfo:
    def __init__(self, url, title=None, jap_title=None, metadata={}):
        self.url = url
        self.title = title
        self.jap_title = jap_title
        self.metadata = metadata

def search_mal(query):

    def search(query):
        soup = helpers.soupify(helpers.get('https://myanimelist.net/anime.php', params = {'q':query}))
        search_results = soup.select("a.hoverinfo_trigger.fw-b.fl-l")
        # URL is only really needed, but good to have title too since MAL can be made non-automatic
        # in the future with a flag if it's bugged
        return [SearchResult(
            url = i.get('href'),
            title = i.select('strong')[0].text
            ) for i in search_results]
        
    def scrape_metadata(url):
        soup = helpers.soupify(helpers.get(url))
        """
        info_dict contains something like this: [{
        'url': 'https://myanimelist.net/anime/37779/Yakusoku_no_Neverland',
        'title': 'The Promised Neverland',
        'jap_title': '約束のネバーランド'
        },{
        'url': 'https://myanimelist.net/anime/39617/Yakusoku_no_Neverland_2nd_Season',
        'title': 'The Promised Neverland 2nd Season',
        'jap_title': '約束のネバーランド 第2期'}]
        """
        info_dict = {
            'url':url
        }

        # Maps specified info in sidebar to variables in info_dict
        name_dict = {
        'Japanese:':'jap_title',
        'English:':'title',
        'synonyms:':'synonyms'
        }

        extra_info = [i.text.strip() for i in soup.select('div.spaceit_pad')]
        for i in extra_info:
            text = i.strip()
            for j in name_dict:
                if text.startswith(j):
                    info_dict[name_dict[j]] = text[len(j):].strip()

        # TODO error message when this stuff is not correctly scraped
        # Can happen if MAL is down or something similar
        return AnimeInfo(url = info_dict['url'], title = info_dict.get('title'),
                jap_title = info_dict.get('jap_title'))
    
    search_results = search(query)
    # Max 10 results
    # season_info = [scrape_metadata(search_results[i].url) for i in range(min(len(search_results), 10))]
    
    # Uses the first result to compare
    season_info = [scrape_metadata(search_results[0].url)] 
    return season_info

def fuzzy_match_metadata(seasons_info, search_results):
    # Gets the SearchResult object with the most similarity title-wise to the first MAL result
    results = []
    for i in seasons_info:
        for j in search_results:
            # 0 if there's no japanese name
            jap_ratio = fuzz.ratio(i.jap_title, j.meta_info['jap_title']) if j.meta_info.get('jap_title') else 0
            # Outputs the max ratio for japanese or english name (0-100)
            ratio = max(fuzz.ratio(i.title,j.title), jap_ratio)
            results.append([ratio,j])

    # Returns the result with highest ratio
    return max(results, key=lambda item:item[0])[1]
    # Should probably be made an object or dict to include the MAL info
