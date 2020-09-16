from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import re
import json


class AnimeTake(Anime, sitename='animetake'):

    sitename = 'animetake'

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(
            helpers.get('https://animetake.tv/search', params={'key': query})
            )

        return [
            SearchResult(
                title=x.find('center').text,
                url='https://animetake.tv{}'.format(x.a['href']),
                )
            for x in soup.select('div.thumbnail')
            ]

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url).text)
        eps = soup.select('a.episode_well_link')
        eps = ['https://animetake.tv{}'.format(x['href']) for x in eps]
        return eps

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url).text)
        self.title = soup.title.text.replace('at AnimeTake', '').strip()


class AnimeTakeEpisode(AnimeEpisode, sitename='animetake'):
    def _get_sources(self):
        soup = helpers.soupify(helpers.get(self.url).text)
        episode_regex = r'gstoreplayer.source\s*=\s*({[\W\w]*?)player.on'
        source = re.search(episode_regex, str(soup))

        validate_json = [
            ['type:', '"type":'], ['sources:', '"sources":'], 
            ['src:', '"src":'], ['size:', '"size":'], 
            ['\n', ''], ['\t', ''], ['],', ']}'], 
            [',}', '}'], ['},]', '}]']]

        source = source.group(1).replace('};', '').replace("'", '"')

        for i in validate_json:
            source = source.replace(i[0], i[1])

        source = json.loads(source)
        videos = source['sources']
        link = 'https://animetake.tv' + videos[-1]['src']
        link = helpers.get(
            link, allow_redirects=False
        ).headers['location']  # gets real link
        return [('no_extractor', link)]
