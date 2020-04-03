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
        soup = helpers.soupify(helpers.get(f"{cls.DOMAIN}browse?q={query}", cf=True))
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
        html = helpers.get(self.url, cf=True).text
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
        soup = helpers.soupify(helpers.get(self.url, cf=True).text)
        self.title = soup.select_one('h2.Title').text


class AnimeflvEpisode(AnimeEpisode, sitename='animeflv'):
    """

    Natsuki and amus are the site's default servers, however amus is not yet implemented here.

    """
    # TODO: Implement support for amus and perhaps Zippyshare?
    # Hint:  https://github.com/Cartmanishere/zippyshare-scraper

    SERVERS = [
        'streamango',
        'natsuki'
    ]

    def _get_sources(self):
        videos = json.loads(
            re.findall('videos = (.*);', helpers.get(self.url, cf=True).text)[0]
        )
        lang = {'subbed': 'SUB', 'latin': 'LAT'}
        videos = videos[lang[self.config.get('version', 'subbed')]]

        server = self.config['server']

        # Trying preferred server from config first
        for video in videos:
            if video['server'] == server:
                if server == 'streamango':
                    return [(server, video['code'])]
                if server == 'natsuki':
                    url = helpers.get(video['code'].replace('embed', 'check')).json()['file']
                    return [('no_extractor', url)]

        logger.debug('Preferred server %s not found.  Trying all supported servers.', server)

        # Trying streamango and natsuki.  The second for loop is not ideal.
        for video in videos:
            if video['server'] == 'streamango':
                return [('streamango', video['code'])]
            if video['server'] == 'natsuki':
                url = helpers.get(video['code'].replace('embed', 'check')).json()['file']
                return [('no_extractor', url)]

        # No supported server found, exit.
        err = 'No supported host server found.  Try another site.'
        args = [self.url]
        raise NotFoundError(err, *args)
