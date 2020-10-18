
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from difflib import get_close_matches
from requests.exceptions import HTTPError
from bs4.element import NavigableString

import re
import requests
import time
import logging
import json

logger = logging.getLogger(__name__)


class EraiRaws(Anime, sitename='erai-raws'):
    sitename = 'erai-raws'
    QUALITIES = ['720p', '1080p']

    # Bypass DDosGuard
    @classmethod
    def bypass(self):
        host = "https://erai-raws.info"
        resp = helpers.get(
            "https://check.ddos-guard.net/check.js", cache=False).text

        # new Image().src = '/.well-known/ddos-guard/id/WaEVEyURh4MduAdI'; -> /.well-known/ddos-guard/id/WaEVEyURh4MduAdI
        ddosBypassPath = re.search("'(.*?)'", resp).groups()[0]
        return helpers.get(host + ddosBypassPath, cache=False).cookies

    def parse(self, server):
        cookies = self.bypass()
        soup = helpers.soupify(helpers.get(server, cookies=cookies))
        # A mix of episodes and folders containing episode
        # Keeping the nodes to check the titles later for quality selection
        linkNodes = soup.select("td[title] > a[href]")
        folderIndices = [i for i, x in enumerate(
            linkNodes) if "folder" in x.get("href")]

        while len(folderIndices) > 0:
            for index in folderIndices:
                link = linkNodes[index].get("href")

                # Sometimes we get a 403 and have to wait for 5 seconds
                for i in range(6):
                    try:
                        soup = helpers.soupify(
                            helpers.get(link, cookies=cookies))
                        break
                    except HTTPError:
                        time.sleep(5)
                        cookies = self.bypass()
                        soup = helpers.soupify(
                            helpers.get(link, cookies=cookies))

                # Replace the folder node with all the nodes of what the folder contains
                linkNodes[index] = soup.select("td[title] > a[href]")

            # Flatten list, e.g. [node, node, [node, node], node] -> [node, node, node, node, node]
            linkNodes = [i for x in linkNodes for i in x]

            # Maybe due to the flattening, but sometimes <a class="responsiveInfoTable" href="https://srv9.erai-ddl3.info/5757d93aae57a6916eed08bc368ad8b7" target="_blank">[Erai-raws] One Piece - 915 [1080p][Multiple Subtitle].mkv</a> becomes [Erai-raws] One Piece - 915 [1080p][Multiple Subtitle].mkv which leads to an error when getting the links
            for x, y in enumerate(linkNodes):
                if type(y) == NavigableString:
                    linkNodes[x] = y.parent

            folderIndices = [i for i, x in enumerate(
                linkNodes) if "folder" in x.get("href")]

        links = [x.get("href") for x in linkNodes if self.quality in x.text]

        return links

    def getTorrents(self, soup, cookies):
        # Clickable nodes, such as: Notifications, Episodes, Batch, etc
        # We are only interested in Episode/Batch
        nodes = soup.select("a.aa_ss")
        episode_nodes = [x for x in nodes if x.text == "Episodes"]
        load = "load_more_0"

        if not episode_nodes:
            logger.warn("Episodic torrents not found, using batch torrents...")
            batch_torrents = [x for x in nodes if x.text == "Batch"]

            if not batch_torrents:
                logger.warning(
                    "Neither episode torrents nor batch torrents were found.")

            load = "load_more_3"

        max_page_regex = "{}_params.*?max_page.*?(\d+)"
        max_page = int(
            re.search(max_page_regex.format(load), str(soup)).group(1))
        max_page_special = int(
            re.search(max_page_regex.format("load_more_2"), str(soup)).group(1))

        post_data = {"action": load}

        # Get data to post and map to query, e.g:
        """
        {
            'anime-list': 'one-piece', 
             ...
            'order': 'DESC'
        }
        """
        post_data["query"] = json.dumps(json.loads(re.search(
            "posts.*?(\{.*?order.*?\})", str(soup)).group(1).replace("\\", "")), separators=(",", ":"))

        episodes = []

        for page in range(max_page + max_page_special):
            post_data["page"] = page if page < max_page else page - max_page

            if page >= max_page:
                post_data["action"] = "load_more_2"

            resp = helpers.post(
                "https://erai-raws.info/wp-admin/admin-ajax.php", data=post_data, cookies=cookies)

            if resp:
                soup = helpers.soupify(resp)

                # List of tuples of (quality, magnet)
                eps = [(x[0].text, x[1]["href"]) for y in [list(zip(x.select("i.sp_p_q"), x.select("a.load_more_links[href*=magnet]")))
                                                           for x in soup.select("article div:has(i.sp_p_q):has(a.load_more_links[href*=magnet])")] for x in y]

                # Filter by quality
                filtered_eps = [x[1] for x in eps if self.quality in x[0]]

                if not filtered_eps:
                    logger.warning(
                        f"Quality {self.quality} not found. Trying {self.QUALITIES[not self.QUALITIES.index(self.quality)]}")
                    filtered_eps = [
                        x[1] for x in eps if self.QUALITIES[not self.QUALITIES.index(self.quality)]]

                for ep in filtered_eps:
                    # Sometimes duplication happens
                    if ep not in episodes:
                        episodes.append(ep)

        return episodes

    @classmethod
    def search(cls, query):
        cookies = cls.bypass()
        soup = helpers.soupify(helpers.get(
            "https://erai-raws.info/anime-list/", cookies=cookies))
        result_data = soup.find(
            "div", {"class": "shows-wrapper"}).find_all("a")
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

        cookies = self.bypass()
        soup = helpers.soupify(helpers.get(self.url, cookies=cookies))

        # Check if anime has DDL - as of writing this, most do not
        ddl = soup.select("div.ddmega > a[href]")[0]

        # As opposed to Subs
        if ddl.text == "DDL":
            server = ddl.get("href")
            return self.parse(server)
        else:
            # use torrent
            logger.warn("Direct download links not found, using torrents...")
            return self.getTorrents(soup, cookies)

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.find("h1").find("span").text


class EraiRawsEpisode(AnimeEpisode, sitename='erai-raws'):
    def _get_sources(self):
        if self.url.startswith("magnet:"):
            return [("no_extractor", self.url)]

        # Headers have to be really good
        headers = {
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/56.0',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'document',
            'referer': self.url,
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en;q=0.9'
        }

        for i in range(4):
            # Using a request session as helpers is lacking the head function, and having a session makes everything more seamless
            session = requests.session()
            resp = session.get(
                self.url, cookies=EraiRaws.bypass(), headers=headers)
            page = resp.text

            """
            Example:
            --------
            $('.download-timer').html("<a class='btn btn-free' href='https://srv9.erai-ddl3.info/486dbafc9628c685c5e67c14d438a425?pt=UmpjMllXWlNSbVl4Vm5CcVNqRnBSVlVyUm5WcVVUMDlPdlF5TEtZVi9TZ2JXc01DOGc2WkhIYz0%3D'>download now</a>");
            """
            download_link = re.search(
                "\.download-timer.*?html.*?href=['\"](.*?)['\"]", page).group(1)

            # Required - if you don't wait, you generally won't get the actual download link
            time.sleep(10)

            resp = session.head(
                download_link, headers=headers, cookies=resp.cookies)

            if resp.status_code == 302:
                download_link = resp.headers.get("location")
                break

            self.url = download_link

        return [("no_extractor", download_link)]
