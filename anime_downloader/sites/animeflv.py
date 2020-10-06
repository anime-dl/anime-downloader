from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from anime_downloader.sites.exceptions import NotFoundError

import re
import json
import logging
import sys

logger = logging.getLogger(__name__)


class Animeflv(Anime, sitename='animeflv'):
    """
    Nice things

    Siteconfig
    ----------

    version: subbed or latin
        subbed for subbed
        latin for Spanish
    server: one of below
        natsuki, streamango

    """
    sitename = 'animeflv'
    QUALITIES = ['360p', '480p', '720p', '1080p']
    DOMAIN = "https://animeflv.net/"

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.get(f"{cls.DOMAIN}browse", params={"q": query}))
        results = [
            SearchResult(title=v.h3.text, url=cls.DOMAIN + v.a['href'], poster=v.img['src'])
            for v in soup.select('ul.ListAnimes > li')
        ]
        return results

    def _scrape_episodes(self):
        # '<a href="/ver/' + episodes[i][1] + '/' + anime_info[2] + '-' + episodes[i][0] + '">'
        #'<h3 class="Title">' + anime_info[1] + '</h3>'
        #'<p>Episodio ' + episodes[i][0] + '</p></a>'
        #'<label for="epi' + episodes[i][0]
        html = helpers.get(self.url).text
        anime_info = json.loads(
            re.findall('anime_info = (.*);', html)[0]
        )
        episodes = json.loads(
            re.findall('episodes = (.*);', html)[0]
        )
        links = [
            self.DOMAIN + f'ver/{epi[1]}/{anime_info[2]}-{epi[0]}'
            for epi in episodes
        ]
        return links[::-1]

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.select_one('h1.Title').text


class AnimeflvEpisode(AnimeEpisode, sitename='animeflv'):
    """

    Natsuki and amus are the site's default servers, however amus is not yet implemented here.

    """
    # TODO: Implement support for amus and perhaps Zippyshare?
    # Hint:  https://github.com/Cartmanishere/zippyshare-scraper

    # TODO add more servers.
    SERVERS = [
        'Stape'
    ]

    def _get_sources(self):
        videos = json.loads(
            re.findall('videos = (.*);', helpers.get(self.url).text)[0]
        )

        lang = {'subbed': 'SUB', 'latin': 'LAT'}
        videos = videos[lang[self.config.get('version', 'subbed')]]

        # Exceptions to domain -> extractor
        extractor_dict = {
            'fembed': 'gcloud',
            'gocdn': 'streamium',
            'yu': 'yourupload',
            'stape': 'streamtape'
        }
        sources_list = []
        for i in videos:
            if i['server'] in self.config['servers']:
                extractor = extractor_dict.get(i['server'], 'no_extractor')
                # Should be extractor to prevent extra requests.
                if i['server'] == 'natsuki':
                    url = helpers.get(video['code'].replace('embed', 'check')).json()['file']
                    extractor = 'no_extractor'

                sources_list.append({
                    'extractor': extractor,
                    'url': i['code'],
                    'server': i['server'],
                    'version': 'subbed'
                })

        return self.sort_sources(sources_list)

        """
        # No supported server found, exit.
        err = 'No supported host server found.  Try another site.'
        args = [self.url]
        raise NotFoundError(err, *args)
        """
