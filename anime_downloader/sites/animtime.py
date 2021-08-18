
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from difflib import get_close_matches

import re


def format_title_case(text):
    """
    Will format text to title case and it will have roman numbers in capital case
    only I is supported so only up to III, any number bigger than that will keep its original capitalization case
    """
    words = text.split()
    new_text = []

    for word in words:
        if word.lower().replace('i', '') == '':
            new_text += ['I' * len(word)]
            continue

        elif word.lower() == 'dub':
            new_text += ['(Dub)']
            continue

        new_text += [word.title()]

    return ' '.join(new_text)


def get_title_dict(script):
    """
    Returns a tuple with two dictionaries
    the 1st one has the anime slugs with their pretty title
    and the 2nd one has the anime slugs with their ids
    """
    script_text = helpers.get(script).text
    title_function = re.search("tm=.*?}", script_text).group()
    titles_dict = {
        x[0]: format_title_case(x[1].replace('-', ' '))
        for x in re.findall(r"\[tm\.([a-zA-Z0-9]+?)\]=function\(\w\)\{return\"[a-zA-Z0-9\.\:/-]+?\/animtime\/([a-zA-Z-]+?)\/", script_text)
    }
    id_dict = {
        x[0]: x[1]
        for x in re.findall(r"t\[t\.(.*?)=(\d+)", title_function)
    }

    for title in id_dict:
        """
        For any anime that are not matched in the pretty titles dictionary (titles_dict)

        for example Bleach (with the id of 1 is not in titles_dict)
        """
        if title not in titles_dict:
            titles_dict[title] = ' '.join(
                re.sub(r"([A-Z])", r" \1", title).split())

    return titles_dict, id_dict


def get_script_link():
    soup = helpers.soupify(helpers.get('https://animtime.com'))
    script = 'https://animtime.com/' + \
        soup.select('script[src*=main]')[0].get('src')

    return script


class AnimTime(Anime, sitename='animtime'):
    sitename = 'animtime'

    @classmethod
    def search(cls, query):
        titles = get_title_dict(get_script_link())
        matches = get_close_matches(query, titles[0], cutoff=0.2)

        search_results = [
            SearchResult(
                title=titles[0].get(match),
                url='https://animtime.com/title/{}'.format(
                    titles[1].get(match))
            )
            for match in matches
        ]

        return search_results

    def _scrape_episodes(self):
        link = get_script_link()
        titles = dict((y, x) for x, y in get_title_dict(link)[1].items())
        current_title = titles.get(self.url.split('/')[-1])

        script_text = helpers.get(link).text
        ep_count = int(re.search(
            r"\[tm\.{}\]=(\d+)".format(current_title.replace(' ', '')), script_text).group(1))

        episodes = []
        for i in range(ep_count):
            episodes.append(self.url + f'/episode/{i + 1}')

        return episodes

    def _scrape_metadata(self):
        titles = get_title_dict(get_script_link())[1]
        self.title = next(x for x, y in titles.items()
                          if int(y) == int(self.url.split('/')[-1]))


class AnimTimeEpisode(AnimeEpisode, sitename='animtime'):
    def _get_sources(self):
        titles = get_title_dict(get_script_link())[1]

        current_title = next(x for x, y in titles.items()
                             if int(y) == int(self.url.split('/')[-3]))
        current_ep = "{0:03}".format(int(self.url.split('/')[-1]))

        script_text = helpers.get(get_script_link()).text
        regexed_link = re.search('tm\.' + current_title.replace(" ", "") +
                                 '\]=function\(.*?return.*?(https.*?)"}', script_text).group(1)
        link = regexed_link.replace('"+t+"', current_ep)

        return [('wasabisys', link)]
