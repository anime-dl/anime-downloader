from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

import re
import json
import logging

logger = logging.getLogger(__name__)


class Animeflv(Anime, sitename='animeflv'):
    """
    Nice things

    Siteconfig
    ----------

    version: subbed or latin
        subbed for subbed
        latin for latin
    server: one of below
        natsuki, streamango, rapidvideo

    """
    sitename = 'animeflv'
    QUALITIES = ['360p', '480p', '720p', '1080p']
    DOMAIN = "https://animeflv.net/"

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.get(f"{cls.DOMAIN}browse?q={query}"))
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
        soup = helpers.soupify(helpers.get(self.url).text)
        self.title = soup.select_one('h2.Title').text


class AnimeflvEpisode(AnimeEpisode, sitename='animeflv'):
    """
    Natsuki no longer appears to be used, but leaving the option here for now.  
    However, it's no longer coded to download from Natsuki, so the option does nothing.
    """
    SERVERS = [
        'streamango',
        'natsuki'
    ]

    def _get_sources(self):

        soup = helpers.soupify(helpers.get(self.url))
        extractors_url = []

        for element in soup.find_all('a', href=re.compile('http://ouo.io/.*streamango.com')):
            extractor_class = 'streamango'
            source_url = element.get('href')
            mux = source_url.split('%2F')
            mux = mux[4]
            source_url = 'https://streamango.com/embed/' + mux
            logger.debug('%s: %s', extractor_class, source_url)
            extractors_url.append((extractor_class, source_url,))
        return extractors_url

        '''
        Previous code below:

        videos = json.loads(
            re.findall('videos = (.*);', helpers.get(self.url).text)[0]
        )
        lang = {'subbed': 'SUB', 'latin': 'LAT'}
        videos = videos[lang[self.config.get('version', 'subbed')]]

        server = self.config['server']
        for video in videos:
            if video['server'] == server:
                logger.debug('video_server: %s', server)
                if server in ['mango']:
                    return [(server, video['code'])]
                if server == 'natsuki':
                    url = helpers.get(video['code'].replace('embed', 'check')).json()['file']
                    return [('no_extractor', url)] 
        '''
