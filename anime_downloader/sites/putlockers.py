from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from urllib.parse import quote_plus

import base64
import re


class PutLockers(Anime, sitename="putlockers"):
    sitename = "putlockers"

    @classmethod
    def search(cls, query):
        search_url = "http://putlockers.fm/search-movies/{}.html".format(
            quote_plus(query))
        soup = helpers.soupify(helpers.get(search_url))

        search_results = [
            SearchResult(
                title=x.find("img").get("alt"),
                url=x.get("href"),
                meta_info={
                    'version_key_dubbed': '(dub)'
                }
            )
            for x in soup.select("div.item > a")
        ]

        return search_results

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        eps = soup.select("a.episode.episode_series_link")
        eps = [i['href'] for i in eps]

        if not eps:
            eps.append(self.url)

        return eps

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.find("h1").text


class PutLockersEpisode(AnimeEpisode, sitename="putlockers"):
    def _get_sources(self):
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/56.0"}
        text = helpers.get(self.url).text

        sources_list = []
        regexed = re.search(r'Base64.decode\("(.*)"\)', text)

        if regexed:
            link = helpers.soupify(base64.b64decode(
                regexed.group(1)).decode()).iframe.get("src")
            sources_list.append({
                "extractor": "eplay",
                "url": link,
                "server": "eplay",
                "version": "dubbed"
            })

        soup = helpers.soupify(text)
        # Cap at 10 servers for the sake of speed
        servers = soup.select("p.server_version a")[:10]

        for server in servers:
            page_link = server.get("href")

            if page_link:
                text = helpers.get(page_link).text
                soup = helpers.soupify(text)
                regexed = re.search(r'Base64.decode\("(.*)"\)', text)
                if regexed:
                    iframe = helpers.soupify(base64.b64decode(
                        regexed.group(1)).decode()).iframe
                    if iframe:
                        link = iframe.get("src")

                        sources_list.append({
                            "extractor": "eplay",
                            "url": link,
                            "server": "eplay",
                            "version": "dubbed"
                        })

                link_node = soup.select("div.mediaplayer a")
                if link_node:
                    link = link_node[0].get("href")

                    # There's also vshare - but that didn't work for me
                    if "mixdrop" in link:
                        sources_list.append({
                            "extractor": "mixdrop",
                            "url": link,
                            "server": "mixdrop",
                            "version": "dubbed"
                        })

        return self.sort_sources(sources_list)
