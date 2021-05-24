import json
import logging
import re
import time
from urllib.parse import unquote

from anime_downloader.config import Config
from anime_downloader.sites import helpers
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult

logger = logging.getLogger(__name__)

NINEANIME_SITE_REGEX = re.compile(r"(?:https?://)?(?:\S+\.)?9anime\.to/watch/[^&?/]+\.(?P<slug>[^&?/]+)")

WAF_TOKEN = re.compile(r"(\d{64})")
WAF_SEPARATOR = re.compile(r"\w{2}")
    
DATA_SOURCE = {
    '28': 'mycloud',
    '41': 'vidstream',
    '40': 'streamtape',
    '35': 'mp4upload'
}
    
def get_waf_cv(html_str_content):
    return ''.join(chr(int(c, 16)) for c in WAF_SEPARATOR.findall(WAF_TOKEN.search(html_str_content).group(1)))

def validate_json_content_yield(session, url, **session_kwargs):
    """
    Use this when the JSON content yield is guarenteed, else, it will request content till eternity.
    
    9Anime throws 500s if fast paced traffic is seen; this function combats that.
    """
    c = False
    while not c:
        time.sleep(.3)
        with session.get(url, **session_kwargs) as response:
            c = response.ok
    
    return json.loads(response.text)
    

class NineAnime(Anime, sitename='nineanime'):
    sitename = '9anime'
    extension = Config['siteconfig'][sitename]['domain_extension']
    url = f'https://{sitename}.{extension}'
    search_url = f"{url}/search"
    server_ajax = "https://%s.%s/ajax/anime/servers" % (sitename, extension)

    def __init__(self, url=None, quality='720p', fallback_qualities=None, _skip_online_data=False, subbed=None):
        session = helpers.request.requests.Session()
        self.session_waf_cv = get_waf_cv(session.get("https://9anime.to/").text)
        super().__init__(url=url, quality=quality, fallback_qualities=fallback_qualities, _skip_online_data=_skip_online_data, subbed=subbed)

    @classmethod
    def search(cls, query):
        session = helpers.request.requests.Session()
        search_waf = get_waf_cv(session.get("https://9anime.to/").text)
        search_results = helpers.soupify(session.get(cls.search_url, params={'keyword': query}, headers={'cookie': 'waf_cv=%s' % search_waf, 'referer': 'https://9anime.to/'})).select('a.name')
        return [
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

    def _scrape_episodes(self):
        self.extension = self.config['domain_extension']
        session = helpers.request.requests.Session()
        content_id = NINEANIME_SITE_REGEX.search(self.url).group('slug')
        access_headers = {
            'cookie': 'waf_cv=%s' % self.session_waf_cv,
            'referer': 'https://9anime.to/',
        }
        servers_ajax = helpers.soupify(validate_json_content_yield(session, self.server_ajax, params={'id': content_id}, headers=access_headers).get('html'))
        
        def fast_yield():
            """
            Internal generator to avoid creating lists and appending to them.
            """
            for element in servers_ajax.select('li > a'):
                data_content = json.loads(element.get('data-sources', '{}'))
                if data_content:
                    yield json.dumps({'sources': data_content, 'waf_cv': self.session_waf_cv})
        
        return [*fast_yield()]

    def _scrape_metadata(self):
        session = helpers.request.requests.Session()
        self.title = helpers.soupify(session.get(self.url, headers={'cookie': 'waf_cv=%s' % self.session_waf_cv, 'referer': 'https://9anime.to/'})).select('h1.title')[0].text

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
            part1 = unquote(part1)
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
        """
        4 API calls to extract content url from all the servers.
        """
        self.extension = self.config['domain_extension']
        
        if not self.url:
            return []
        
        session = helpers.request.requests.Session()
        data = json.loads(self.url) # type: dict[str, str]
        episode_source_ajax = "https://9anime.%s/ajax/anime/episode" % self.extension
        
        def fast_yield():
            sources = data.get('sources', {})
            for data_source, id_hash in sources.items():
                url = validate_json_content_yield(session, episode_source_ajax, params={'id': id_hash}, headers={'cookie': 'waf_cv=%s' % data.get('waf_cv', '')}).get('url', '')
                yield (DATA_SOURCE.get(data_source, ''), self.decodeString(url))
                
        return [*fast_yield()]
