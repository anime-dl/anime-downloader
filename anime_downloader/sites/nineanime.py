import time
import logging
import re

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)

class NineAnime(Anime, sitename='9anime'):
        sitename = '9anime'
        url = f'https://{sitename}.to/search'
        @classmethod
        def search(cls, query):
            # Only uses the first page of search results, but it's sufficent.
            search_results = helpers.soupify(helpers.get(cls.url, params={'keyword': query})).select('a.name')
            return [
                SearchResult(
                    title = i.text,
                    url = i.get('href')
                    )
                for i in search_results
            ]


        def _scrape_episodes(self):
            soup = helpers.soupify(helpers.get(self.url))
            # Assumptions can cause errors, but if this fails it's better to get issues on github.
            title_id = soup.select("div#player")[0]
            title_id = title_id.get('data-id')
            episode_html = helpers.get(f"https://9anime.to/ajax/film/servers?id={title_id}").text
            # Only using streamtape, MyCloud can get added, but it uses m3u8.
            streamtape_regex = r'data-id=\\"40\\".*?(data-name|$)'
            streamtape_episodes = re.search(streamtape_regex, episode_html)
            if not streamtape_episodes:
                logger.error('Unable to find streamtape server')
                return ['']

            streamtape_episodes = streamtape_episodes.group()
            # You can use helpers.soupify on all this, but it's resource intensive, unreliable
            # and can give recursion errors on large series like naruto.

            # Group 3 is the actual id.
            # Matches stuff like: id=\"a9cfdbd2029a467d2b2c9f156cbedc02b25a23199812ad4dbe5a25afa9edb140\"
            episode_regex = r'id=(\\|)(\'|")(.{64}?)(\\|)(\'|")'
            episodes = re.findall(episode_regex, streamtape_episodes)
            if not episodes:
                logger.error('Unable to find any episodes')
                return ['']

            # Returns an ID instead of actual URL
            return [i[2] for i in episodes]


        def _scrape_metadata(self):
            self.title = helpers.soupify(helpers.get(self.url)).select('h1.title')[0].text


class NineAnimeEpisode(AnimeEpisode, sitename='9anime'):
        def _get_sources(self):
            if not self.url:
                return ''

            # Arbitrary timeout to prevent spamming the server which will result in an error.
            time.sleep(0.3)
            # Server 40 is streamtape, change this if you want to add other servers
            episode_ajax = f"https://9anime.to/ajax/episode/info?id={self.url}&server=40"
            target = helpers.get(episode_ajax).json().get('target','')
            logger.debug('Videolink: {}'.format(target))
            if not target:
                return ''

            videolink = helpers.soupify(helpers.get(target)).select('div#videolink')
            logger.debug('Videolink: {}'.format(videolink))
            if not videolink:
                return ''

            videolink = videolink[0].text

            # Appends https
            videolink = 'https:' + videolink if videolink.startswith('//') else videolink
            return [('no_extractor', videolink,)]
