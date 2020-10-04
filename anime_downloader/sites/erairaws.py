
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from difflib import get_close_matches

import re
import logging

logger = logging.getLogger(__name__)


class EraiRaws(Anime, sitename='erai-raws'):
    sitename = 'erai-raws'
    QUALITIES = ['720p', '1080p']

    # Bypass DDosGuard
    @classmethod
    def bypass(self):
        host = "https://erai-raws.info"
        resp = helpers.get("https://check.ddos-guard.net/check.js").text

        # new Image().src = '/.well-known/ddos-guard/id/WaEVEyURh4MduAdI'; -> /.well-known/ddos-guard/id/WaEVEyURh4MduAdI
        ddosBypassPath = re.search("'(.*?)'", resp).groups()[0]
        return helpers.get(host + ddosBypassPath).cookies

    def parse(self, server, cookies):
        soup=helpers.soupify(helpers.get(server, cookies=cookies))
        # A mix of episodes and folders containing episodes
        links=[x.get("href") for x in soup.select("td[title] > a[href]")]
        folderIndices=[i for i, x in enumerate(links) if "folder" in x]

        for index in folderIndices:


    @classmethod
    def search(cls, query):
        cookies=cls.bypass()
        soup = helpers.soupify(helpers.get("https://erai-raws.info/anime-list/", cookies=cookies))
        result_data = soup.find("div", {"class": "shows-wrapper"}).find_all("a")
        titles = [x.text.strip() for x in result_data]

        # Erai-raws doesnt have a search that I could find - so I've opted to implement it myself
        titles = get_close_matches(query, titles, cutoff=0.2)
        result_data = [x for x in result_data if x.text.strip() in titles]

        search_results = [
            SearchResult(
                title=result.text.strip(),
                url="https://erai-raws.info/anime-list/" + result.get("href")
            )
            for result in result_data
        ]
        return search_results

    def _scrape_episodes(self):
        if self.quality not in self.QUALITIES:
            self.quality = "720p"

        cookies=self.bypass()
        soup = helpers.soupify(helpers.get(self.url, cookies=cookies))

        #Check if anime has DDL - as of writing this, most do not
        ddl=soup.select("div.ddmega > a[href]")[0]

        # As opposed to Subs
        if ddl.text == "DDL":
            server=ddl.get("href")
            return self.parse(server, cookies)
        else:
            # use torrent
            logger.warn("Direct download links not found, using torrent...")
            return self.getTorrents(soup, cookies)

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.find("h1").find("span").text


class EraiRawsEpisode(AnimeEpisode, sitename='erai-raws'):
    def _get_sources(self):
        if self.url.startswith("magnet:"):
            return [("no_extractor", self.url)]


