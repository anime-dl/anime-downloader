
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from difflib import get_close_matches
import base64

class EraiRaws(Anime, sitename='erai-raws'):
    sitename='erai-raws'
    QUALITIES = ['720p', '1080p']

    #Bypass DDosGuard
    def bypass(self):
        host = "https://erai-raws.info"
        url = "https://erai-raws.info/anime-list/"
        u = base64.b64encode(url.encode('utf-8'))
        h = base64.b64encode(host.encode('utf-8'))
        bypass_link = helpers.post('https://ddgu.ddos-guard.net/ddgu/', data = {'u':u, 'h':h, 'p':''}, headers = {'Referer': url}, allow_redirects = False).headers["Location"]
        helpers.get(bypass_link, allow_redirects = False)

    def parse(self, rows, url):
        episodes = []

        if self.quality == self.QUALITIES[0]:
            rows = rows[::2]
        else:
            rows = rows[1::2]

        for row in rows:
            if row.parent.get("href")[-3:] != "mkv":
                folder = helpers.soupify(helpers.get(url + row.parent.get("href")))

                #Append all episodes in folder - folders are also seperated by quality
                #So everything in a folder can be taken in one go
                [episodes.append(url[:-9] + x.parent.get("href")) for x in folder.find("ul", {"id":"directory-listing"}).find_all("div", {"class":"row"})]
            else:
                episodes.append(url[:-9] + row.parent.get("href"))
        return episodes[1:]

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
        files = files + "index.php"
        html = helpers.get(files)
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
