
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from difflib import get_close_matches
import re

class EraiRaws(Anime, sitename='erai-raws'):
    sitename='erai-raws'
    QUALITIES = ['720p', '1080p']

    #Bypass DDosGuard
    def bypass(self):
        host = "https://erai-raws.info"
        resp = helpers.get("https://check.ddos-guard.net/check.js").text
        ddosBypassPath = re.search("'(.*?)'", resp).groups()[0]
        helpers.get(host + ddosBypassPath)

    def parse(self, rows, url):
        episodes = []

        if self.quality == self.QUALITIES[0] and len(rows) > 1:
            rows = rows[::2]
        elif len(rows) > 1:
            rows = rows[1::2]

        for row in rows:
            if row.parent.get("href")[-3:] != "mkv":
                if url[-1] != '/':
                    url = url + '/'
                folder = helpers.get(url + "index.php" + row.parent.get("href"))
                folder = helpers.soupify(folder)

                #Append all episodes in folder - folders are also seperated by quality
                #So everything in a folder can be taken in one go
                [episodes.append(url + x.parent.get("href")) for x in folder.find("ul", {"id":"directory-listing"}).find_all("div", {"class":"row"})]
            else:
                episodes.append(url + row.parent.get("href"))

        episodes = episodes[1:]

        if len(rows) == 1:
            if rows[0].parent.get("href")[-3:] != "mkv":
                url = f"{url}index.php" if url[:-1] == "/" else f"{url}/index.php"
                folder = helpers.soupify(helpers.get(url + rows[0].parent.get("href")))
                episodes = [url + x.parent.get("href") for x in folder.find("ul", {"id":"directory-listing"}).find_all("div", {"class":"row"})]
            else:
                episodes = [url + rows[0].parent["href"]]

        return episodes

    @classmethod
    def search(cls, query):
        cls.bypass(cls)
        soup = helpers.soupify(helpers.get("https://erai-raws.info/anime-list/"))
        result_data = soup.find("div", {"class":"shows-wrapper"}).find_all("a")
        titles = [x.text.strip() for x in result_data]

        #Erai-raws doesnt have a search that I could find - so I've opted to implement it myself
        titles = get_close_matches(query, titles, cutoff=0.2)
        result_data = [x for x in result_data if x.text.strip() in titles]

        search_results = [
            SearchResult(
                title = result.text.strip(),
                url = "https://erai-raws.info/anime-list/" + result.get("href")
                )
            for result in result_data
            ]
        return search_results

    def _scrape_episodes(self):
        self.bypass()
        soup = helpers.soupify(helpers.get(self.url))
        files = soup.find("div", {"class":"ddmega"}).find("a").get("href")
        if files[-1] != '/':
            files = files + '/'
        index = files + "index.php"
        html = helpers.get(index, headers = {"Referer":files})
        soup = helpers.soupify(html)
        rows = soup.find("ul", {"id":"directory-listing"}).find_all("div", {"class":"row"})
        episodes = self.parse(rows, files)
        return episodes

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.find("h1").find("span").text

class EraiRawsEpisode(AnimeEpisode, sitename='erai-raws'):
    def _get_sources(self):
        return [("no_extractor", self.url)]
