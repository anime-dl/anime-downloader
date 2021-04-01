
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from difflib import get_close_matches

import re


class AnimTime(Anime, sitename='animtime'):
    sitename = 'animtime'

    @classmethod
    def get_title_dict(cls, script):
        script_text = helpers.get(script).text
        title_function = re.search("tm=.*?}", script_text).group()
        titles_regexed = re.findall("t\[t\.(.*?)=(\d+)", title_function)
        titles = dict([(' '.join(re.sub(r"([A-Z])", r" \1", x[0]).split()), x[1])
                       for x in titles_regexed])

        return titles

    @classmethod
    def get_script_link(cls):
        soup = helpers.soupify(helpers.get('https://animtime.com'))
        script = 'https://animtime.com/' + \
            soup.select('script[src*=main]')[0].get('src')

        return script

    @classmethod
    def search(cls, query):
        titles = cls.get_title_dict(cls.get_script_link())
        matches = get_close_matches(query, titles, cutoff=0.2)

        search_results = [
            SearchResult(
                title=match,
                url='https://animtime.com/title/{}'.format(titles.get(match))
            )
            for match in matches
        ]

        return search_results

    def _scrape_episodes(self):
        link = self.get_script_link()
        titles = dict((y, x) for x, y in self.get_title_dict(link).items())
        current_title = titles.get(self.url.split('/')[-1])

        script_text = helpers.get(link).text
        ep_count = int(re.search(
            "zd\[tm\.{}\]=(\d+)".format(current_title.replace(' ', '')), script_text).group(1))

        episodes = []
        for i in range(ep_count):
            episodes.append(self.url + f'/episode/{i + 1}')

        return episodes

    def _scrape_metadata(self):
        titles = dict((y, x) for (x, y) in self.get_title_dict(
            self.get_script_link()).items())
        self.title = titles.get(self.url.split('/')[-1])


class AnimTimeEpisode(AnimeEpisode, sitename='animtime'):
    def _get_sources(self):
        titles = dict((y, x) for x, y in AnimTime.get_title_dict(
            AnimTime.get_script_link()).items())
        current_title = titles.get(self.url.split('/')[-3])
        current_ep = "{0:03}".format(int(self.url.split('/')[-1]))

        script_text = helpers.get(AnimTime.get_script_link()).text
        regexed_link = re.search('tm\.' + current_title.replace(" ", "") +
                                 '\]=function\(.*?return.*?(https.*?)"}', script_text).group(1)
        link = regexed_link.replace('"+t+"', current_ep)

        return [('wasabisys', link)]
