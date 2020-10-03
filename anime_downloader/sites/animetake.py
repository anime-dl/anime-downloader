from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import re
import json
import logging

logger = logging.getLogger(__name__)


class AnimeTake(Anime, sitename='animetake'):

    sitename = 'animetake'

    @classmethod
    def search(cls, query):
        # Due to how search works some titles cannot get found by the search.
        # For example the one piece movies only shows up while in the once piece tab.
        soup = helpers.soupify(
            helpers.get('https://animetake.tv/search', params={'key': query})
        )

        return [
            SearchResult(
                title=x.find('center').text.strip(),
                url='https://animetake.tv{}'.format(x.a['href']),
                meta_info={
                    'version_key_dubbed': '(Dubbed)'
                })
            for x in soup.select('div.thumbnail')
        ]

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        eps = soup.select('a.episode_well_link')
        # Sometimes the episodes are listed in reverse (One Piece)
        # Will reverse movies, but shouldn't matter.
        reverse = "Episode 1" not in eps[0].text
        eps = ['https://animetake.tv{}'.format(x['href']) for x in eps]

        if reverse:
            eps.reverse()

        return eps

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.title.text.replace('at AnimeTake', '').strip()


class AnimeTakeEpisode(AnimeEpisode, sitename='animetake'):
    def _get_sources(self):
        soup = helpers.soupify(helpers.get(self.url))

        gstore_regex = r'gstoreplayer\.source\s*=\s*({[\W\w]*?);'
        servers = self.config['servers']
        logger.debug('Config {}'.format(self.config))

        # Mapping servers to extractors.
        extractor_dict = {
            'vidstreaming': 'vidstream',
            'fembed': 'gcloud'
        }

        links = []
        gstore_source = re.search(gstore_regex, str(soup))

        # No idea if 2 player
        if gstore_source:
            source = gstore_source.group(1)
            # All this fuckery below to fix the semi broken json.

            # This removes all whitespace.
            source = re.sub(r'\s', '', source)
            regex = r"[{|,][\s]*?[\w]*?[^\"']:"
            # replaces file: with "file":
            for i in re.findall(regex, source):
                source = source.replace(i, f'{i[:1]}"{i[1:-1]}"{i[-1:]}')
            # Removes ' and , which will error on the strict python json formatter.
            source = source.replace("'", '"').replace(',}', '}').replace(',]', ']')

            source = json.loads(source)
            videos = source['sources']
            link = self.get_real_url('https://animetake.tv' + videos[-1]['src'])
            links.append({
                         'url': link,
                         'extractor': 'no_extractor',
                         'server': 'gstore',
                         'version': 'subbed'
                         })

        iframe_regex = r'[\W\w]{0,50}src\s*=\s*"(/redirect[^"]*)'
        for server in servers:
            if server == 'gstore':
                # The server above
                continue

            # Produces the regex based on server name.
            source_regex = server + iframe_regex
            result = re.search(source_regex, str(soup))
            if result:
                link = self.get_real_url('https://animetake.tv' + result.group(1))
                links.append({
                             'url': link,
                             'extractor': extractor_dict.get(server, server),
                             'server': server,
                             'version': 'subbed'
                             })

        return self.sort_sources(links)

    # Real links are hidden behind a redirect link.
    def get_real_url(self, url):
        logger.debug('Redirect link: {}'.format(url))
        url = helpers.get(
            url, allow_redirects=False
        ).headers['location']
        return url
