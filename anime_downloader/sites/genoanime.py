
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers


class GenoAnime(Anime, sitename="genoanime"):
    sitename = "genoanime"

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.post(
            "https://genoanime.com/data/searchdata.php", data={"anime": query}))

        search_results = [
            SearchResult(
                title=x.text,
                url=x.get("href").replace("./", "https://genoanime.com/")
            )
            for x in soup.select("h5 > a[href]")
        ]

        return search_results

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        links = [x.get("href").replace("./", "https://genoanime.com/")
                 for x in soup.select("a.episode[href]")]

        # Conveniently always ends in episode=1 even for movies
        return [(int(x.split("=")[-1]), x) for x in links]

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.h3.text


class GenoAnimeEpisode(AnimeEpisode, sitename='genoanime'):
    def _get_sources(self):
        soup = helpers.soupify(helpers.get(self.url))
        soup = helpers.soupify(helpers.get(soup.iframe.get("src")))
        return [("no_extractor", soup.source.get("src"))]
