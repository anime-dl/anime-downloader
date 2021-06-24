from anime_downloader.sites.helpers.request import post
import logging
import json
import requests
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)
ld = logger.debug

class Batchddl(Anime, sitename='batchddl'):
    sitename = "batchddl"
    @classmethod
    def search(cls, query):
        params = {
            "q" : f"{query}",
        }
        res = helpers.post(r"https://animebatchddl.excalibur-morgan.workers.dev/0:search", data = json.dumps(params), cache=False)
        jsonify = json.loads(res.text)
        testLst = list()
        i = 0
        for a in jsonify["data"]["files"]:
            if a["mimeType"] == "application/vnd.google-apps.folder":
                i += 1
                if i >= 30:
                    break
                postURL = "https://animebatchddl.excalibur-morgan.workers.dev/0:id2path"
                data = json.dumps({"id":a["id"]})
                posted = json.dumps(helpers.post(postURL, data = data, cache=False).text)
                testLst.append([posted.replace("\"", ""), a["name"]])


        search_results = [
            SearchResult(
                title=result[1],
                url="https://animebatchddl.excalibur-morgan.workers.dev/0:" + result[0] + "#"
            )
            for result in testLst
        ]

        return search_results

    def _scrape_episodes(self):
        url = self.url
        data = json.loads(helpers.post(url, json={"q":"","password":None,"page_token":None,"page_index":0}, cache=False).text)
        #ld(data)
        episodes = list()
        for i in data["data"]["files"]:
            if i["mimeType"] == "video/x-matroska":
                postURL = "https://animebatchddl.excalibur-morgan.workers.dev/0:id2path"
                data = json.dumps({"id":i["id"]})
                posted = helpers.post(postURL, data = data, cache=False).text
                episodes.append("https://animebatchddl.excalibur-morgan.workers.dev/0:" + posted)

        return episodes
        #return ["ha", "haha", "hahaha"]


class BatchddlEpisode(AnimeEpisode, sitename='batchddl'):
    sitename = "batchddl"
    def _get_sources(self):
        return [('no_extractor', self.url)]