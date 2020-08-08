from anime_downloader.sites import helpers
import logging
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import get_anime_class
from anime_downloader.config import Config
from anime_downloader.util import primitive_search

import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from fuzzywuzzy import fuzz

logger = logging.getLogger(__name__)

class AnimeInfo:
    """
    Attributes
    ----------
    url: string
        URL for the info page
    title: string
        English name of the show.
    jp_title: string
        Japanase name of the show.
    metadata: dict
        Data not critical for core functions
    episodes: int
        Max amount of episodes
    """
    def __init__(self, url, episodes,title=None, jp_title=None, metadata={}):
        self.url = url
        self.episodes = episodes
        self.title = title
        self.jp_title = jp_title
        self.metadata = metadata


class MatchObject:
    """
    Attributes
    ----------
    AnimeInfo: object
        Metadata object from the MAL search.
    SearchResult: object
        Metadata object from the provider search
    ratio: int
        A number between 0-100 describing the similarities between SearchResult and AnimeInfo.
        Higher number = more similar.
    """
    def __init__(self, AnimeInfo, SearchResult, ratio = 100):
        self.AnimeInfo = AnimeInfo
        self.SearchResult = SearchResult
        self.ratio = ratio

# Not used
def search_mal(query):

    def search(query):
        soup = helpers.soupify(helpers.get('https://myanimelist.net/anime.php', params = {'q':query}))
        search_results = soup.select("a.hoverinfo_trigger.fw-b.fl-l")
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
        'jp_title': '約束のネバーランド'
        },{
        'url': 'https://myanimelist.net/anime/39617/Yakusoku_no_Neverland_2nd_Season',
        'title': 'The Promised Neverland 2nd Season',
        'jp_title': '約束のネバーランド 第2期'}]
        """
        info_dict = {
            'url':url
        }

        # Maps specified info in sidebar to variables in info_dict
        name_dict = {
        'Japanese:':'jp_title',
        'English:':'title',
        'synonyms:':'synonyms',
        'Episodes:':'episodes'
        }
        info = soup.select('span.dark_text')
        extra_info = [i.parent.text.strip() for i in info]
        for i in extra_info:
            text = i.replace('\n','').strip()
            for j in name_dict:
                if text.startswith(j):
                    info_dict[name_dict[j]] = text[len(j):].strip()

        # Backup name if no English name isn't registered in sidebar
        if not info_dict.get('title'):
            name = soup.select('span[itemprop=name]')
            info_dict['title'] = name[0].text if name else None

        # Always sets episodes
        if not info_dict.get('episodes') or info_dict.get('episodes') == 'Unknown':
            info_dict['episodes'] = 0

        # TODO error message when this stuff is not correctly scraped
        # Can happen if MAL is down or something similar
        return AnimeInfo(url = info_dict['url'], title = info_dict.get('title'),
                jp_title = info_dict.get('jp_title'), episodes = int(info_dict['episodes']))

    search_results = search(query)
    season_info = []
    # Max 10 results
    for i in range(min(len(search_results), 10)):
        anime_info = scrape_metadata(search_results[i].url)
        if anime_info.episodes:
            season_info.append(anime_info)

    # Code below uses the first result to compare
    #season_info = [scrape_metadata(search_results[0].url)] 
    #return season_info

    # Prompts the user for selection
    return primitive_search(season_info)


def search_anilist(query):

    def search(query):
        ani_query = """
            query ($id: Int, $page: Int, $search: String, $type: MediaType) {
                Page (page: $page, perPage: 10) {
                    media (id: $id, search: $search, type: $type) {
                        id
                        idMal
                        description(asHtml: false)
                        seasonYear
                        title {
                            english
                            romaji
                            native
                        }
                        coverImage {
                            extraLarge
                        }
                        bannerImage
                        averageScore
                        status
                        episodes
                        }
                    }
                }
            """
        url = 'https://graphql.anilist.co'
        
        # TODO check in case there's no results
        # It seems to error on no results (anime -ll DEBUG dl "nev")
        results = helpers.post(url, json={'query': ani_query, 'variables': {'search': query, 'page': 1, 'type': 'ANIME'}}).json()['data']['Page']['media']
        if not results:
            logger.error('No results found in anilist')
            raise NameError

        search_results = [AnimeInfo(url = 'https://anilist.co/anime/' + str(i['id']), title = i['title']['romaji'],
                jp_title = i['title']['native'], episodes = int(i['episodes'])) for i in results if i['episodes'] != None]
        return search_results

    search_results = search(query)
    # Prompts the user for selection
    return primitive_search(search_results)


def fuzzy_match_metadata(seasons_info, search_results):
    # Gets the SearchResult object with the most similarity title-wise to the first MAL/Anilist result
    results = []
    for i in seasons_info:
        for j in search_results:
            # Allows for returning of cleaned title by the provider using 'title_cleaned' in meta_info.
            # To make fuzzy matching better.
            title_provider = j.title.strip() if not j.meta_info.get('title_cleaned') else j.meta_info.get('title_cleaned').strip()
            # On some titles this will be None
            # causing errors below
            title_info = i.title

            # Essentially adds the chosen key to the query if the version is in use
            # Dirty solution, but should work pretty well

            config = Config['siteconfig'].get(get_anime_class(j.url).sitename,{})
            version = config.get('version')
            version_use = version == 'dubbed'
            # Adds something like (Sub) or (Dub) to the title
            key_used = j.meta_info.get('version_key_dubbed','') if version_use else j.meta_info.get('version_key_subbed','')
            title_info += ' ' + key_used
            title_info = title_info.strip()

            # TODO add synonyms
            # 0 if there's no japanese name
            jap_ratio = fuzz.ratio(i.jp_title, j.meta_info['jp_title']) if j.meta_info.get('jp_title') else 0
            # Outputs the max ratio for japanese or english name (0-100)
            ratio = max(fuzz.ratio(title_info,title_provider), jap_ratio)
            logger.debug('Ratio: {}, Info title: {}, Provider Title: {}, Key used: {}'.format(ratio, title_info, title_provider, key_used))
            results.append(MatchObject(i, j, ratio))

    # Returns the result with highest ratio
    return max(results, key=lambda item:item.ratio)
