
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from difflib import get_close_matches
from requests.exceptions import HTTPError
from bs4.element import NavigableString

import re
import time
import logging

logger = logging.getLogger(__name__)


class EraiRaws(Anime, sitename='erai-raws'):
    sitename = 'erai-raws'
    QUALITIES = ['720p', '1080p']

    # Bypass DDosGuard
    @classmethod
    def bypass(self):
        host = "https://erai-raws.info"
        resp = helpers.get("https://check.ddos-guard.net/check.js", cache=False).text

        # new Image().src = '/.well-known/ddos-guard/id/WaEVEyURh4MduAdI'; -> /.well-known/ddos-guard/id/WaEVEyURh4MduAdI
        ddosBypassPath = re.search("'(.*?)'", resp).groups()[0]
        return helpers.get(host + ddosBypassPath, cache=False).cookies

    def parse(self, server):
        cookies=self.bypass()
        soup=helpers.soupify(helpers.get(server, cookies=cookies))
        # A mix of episodes and folders containing episode
        # Keeping the nodes to check the titles later for quality selection
        linkNodes=soup.select("td[title] > a[href]")
        folderIndices=[i for i, x in enumerate(linkNodes) if "folder" in x.get("href")]

        while len(folderIndices) > 0:
            for index in folderIndices:
                link=linkNodes[index].get("href")

                # Sometimes we get a 403 and have to wait for 5 seconds
                try:
                    soup=helpers.soupify(helpers.get(link, cookies=cookies))
                except HTTPError:
                    time.sleep(5)
                    cookies=self.bypass()
                    soup=helpers.soupify(helpers.get(link, cookies=cookies))
                
                # Replace the folder node with all the nodes of what the folder contains
                linkNodes[index]=soup.select("td[title] > a[href]")

            # Flatten list, e.g. [node, node, [node, node], node] -> [node, node, node, node, node]
            linkNodes=[i for x in linkNodes for i in x]

            # Maybe due to the flattening, but sometimes <a class="responsiveInfoTable" href="https://srv9.erai-ddl3.info/5757d93aae57a6916eed08bc368ad8b7" target="_blank">[Erai-raws] One Piece - 915 [1080p][Multiple Subtitle].mkv</a> becomes [Erai-raws] One Piece - 915 [1080p][Multiple Subtitle].mkv which leads to an error when getting the links
            for x, y in enumerate(linkNodes):
                if type(y) == NavigableString:
                    linkNodes[x] = y.parent

            folderIndices=[i for i, x in enumerate(linkNodes) if "folder" in x.get("href")]

        links=[x.get("href") for x in linkNodes if self.quality in x.text]

        return links

    def getTorrents(self):
        pass

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
            return self.parse(server)
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

        logger.info(helpers.get(self.url).text)
