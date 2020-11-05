import time
import logging
import re
import json

from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from anime_downloader.config import Config
logger = logging.getLogger(__name__)


class NineAnime(Anime, sitename='nineanime'):
    sitename = '9anime'
    extension = Config['siteconfig'][sitename]['domain_extension']
    url = f'https://{sitename}.{extension}'
    search_url = f"{url}/search"

    @classmethod
    def search(cls, query):
        # Only uses the first page of search results, but it's sufficent.
        search_results = helpers.soupify(helpers.get(cls.search_url, params={'keyword': query})).select('a.name')
        search_results = [
            SearchResult(
                title=i.text,
                url= cls.url + i.get('href') if i.get("href").startswith("/") else i.get("href"),
                meta_info={
                    'version_key_dubbed': '(Dub)',
                    'version_key_subbed': ''
                }
            )
            for i in search_results
        ]

        return search_results

    def _scrape_episodes(self):
        self.extension = self.config['domain_extension']
        soup = helpers.soupify(helpers.get(self.url))
        # Assumptions can cause errors, but if this fails it's better to get issues on github.
        title_id = soup.select("div.player-wrapper")[0]
        title_id = title_id.get('data-id')
        episode_html = helpers.get(f"https://9anime.{self.extension}/ajax/anime/servers?id={title_id}").text
        # Only using streamtape, MyCloud can get added, but it uses m3u8.
        streamtape_regex = r'data-sources=[\'"](.*?"40".*?".*?".*?\})'
        streamtape_episodes = re.findall(streamtape_regex, episode_html)

        if not streamtape_episodes:
            logger.error('Unable to find streamtape server')
            return ['']

        episodes = [json.loads(x)['40'] for x in streamtape_episodes]

        if not episodes:
            logger.error('Unable to find any episodes')
            return ['']

        # Returns an ID instead of actual URL
        return episodes

    def _scrape_metadata(self):
        self.title = helpers.soupify(helpers.get(self.url)).select('h1.title')[0].text


class NineAnimeEpisode(AnimeEpisode, sitename='9anime'):
    """
    Decodes the encoded string returned by /ajax/anime/episodes to the embed url.

    Python implementation of decode9AnimeURL, it's basically identical to the js one
    """
    def decodeString(self, str):
        str1 = str[0:9]
        str2 = str[9:]

        encodedNum = 0
        counter = 0
        part1 = ""

        for char in str2:
            encodedNum <<= 6;

            try:
                letterNum = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'.index(char)
                encodedNum |= letterNum
            except:
                pass

            counter += 1

            if counter == 4:
                part1 += chr((16711680 & encodedNum) >> 16)
                part1 += chr((65280 & encodedNum) >> 8)
                part1 += chr(255 & encodedNum)

                encodedNum = 0
                counter = 0

        if counter == 2:
            encodedNum >>= 4
            part1 += chr(encodedNum)
        elif counter == 3:
            encodedNum >>2
            part1 += chr((65280 & encodedNum) >> 8)
            part1 += chr(255 & encodedNum)

        try:
            part1 = urllib.parse.unquote(part1)
        except:
            pass

        arr = {}
        i = 0
        byteSize = 256
        final = ""

        for c in range(byteSize):
            arr[c] = c

        x = 0
        for c in range(byteSize):
            x = (x + arr[c] + ord(str1[c % len(str1)])) % byteSize
            i = arr[c]
            arr[c] = arr[x]
            arr[x] = i

        x = 0
        d = 0

        for s in range(len(part1)):
            d = (d + 1) % byteSize
            x = (x + arr[d]) % byteSize

            i = arr[d]
            arr[d] = arr[x]
            arr[x] = i

            final += chr(ord(part1[s]) ^ arr[(arr[d] + arr[x]) % byteSize])

        return final

    def _get_sources(self):
        self.extension = self.config['domain_extension']
        if not self.url:
            return ''

        # Arbitrary timeout to prevent spamming the server which will result in an error.
        time.sleep(0.3)
        # Server 40 is streamtape, change this if you want to add other servers
        episode_ajax = f"https://9anime.{self.extension}/ajax/anime/episode?id={self.url}"
        target = self.decodeString(helpers.get(episode_ajax).json().get('url', ''))

        logger.debug('Videolink: {}'.format(target))
        if not target:
            return ''

        # Appends https
        return [('streamtape', target)]
