from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

import re
import json

class AnimeSuge(Anime, sitename="animesuge"):
    sitename = "animesuge"

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.get("https://animesuge.io/ajax/anime/search", params={"keyword": query}).json()['html'])

        search_results = [
            SearchResult(
                title=x.find("div").text,
                url="https://animesuge.io" + x.get('href')
            )
            for x in soup.select("a:not(.more)")
        ]

        return search_results

    def _scrape_episodes(self):
        ep_url = "https://animesuge.io/ajax/anime/servers"
        _id = re.search(r".*-(.*)", self.url).group(1)

        soup = helpers.soupify(helpers.get(ep_url, params={'id': _id}))

        return ['https://animesuge.io' + x.get('href') for x in soup.select('a:not(.more)')]

    def _scrape_metadata(self):
        self.title = helpers.soupify(helpers.get(self.url)).find("h1").text


class AnimeSugeEpisode(AnimeEpisode, sitename='animesuge'):
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
        # Get id and ep no. from url, e.g: https://animesuge.io/anime/naruto-xx8z/ep-190 -> xx8z, 190
        _id, ep_no = re.search(r".*\/anime\/.*-(.*?)\/.*-(\d+)$", self.url).group(1, 2)

        # Get sources json from html, e.g:
        """
        <a class="active" data-base="190" data-name-normalized="190" data-sources='{"28":"8e663a9230406b753ba778dba15c723b3bf221b61fbdde6e8adae899adbad7ab","40":"565ff0ca78263f80a8f8a344e06085854f87e3449e321032425498b9d129dbf0","35":"c800a3ec0dfe68265d685792375169007b74c89aa13849869a16a3674d971f45"}' href="/anime/naruto-xx8z/ep-190">190</a>"""
        data_sources = json.loads(helpers.soupify(helpers.get("https://animesuge.io/ajax/anime/servers",
                                  params={"id": _id, "episode": ep_no})).select(f"a[data-base='{ep_no}']")[0].get("data-sources"))

        # Only includes supported
        # Unsupported ones {'28': 'openstream'}
        id_source_map = {'35': 'mp4upload', '40': 'streamtape'}

        sources_list = []
        for key in id_source_map:
            if key in data_sources.keys():
                _id = data_sources[key]

                for _ in range(3):
                    try:
                        link = helpers.get("https://animesuge.io/ajax/anime/episode",
                                           params={"id": _id}).json()['url']
                        break
                    # Makes it more consistent.
                    except HTTPError:
                        time.sleep(5)
                        continue

                server = id_source_map[key]
                sources_list.append({
                    'extractor': server,
                    'url': self.decodeString(link),
                    'server': server,
                    # This may not be true, can't see the info on page.
                    'version': 'subbed'
                })

        return self.sort_sources(sources_list)
