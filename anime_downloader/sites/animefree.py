import logging
import re
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)


class AnimeFree(Anime, sitename='animefree'):
    sitename = 'kissanimefree'
    url = f'https://{sitename}.net/'

    @classmethod
    def search(cls, query):
        search_results = helpers.soupify(helpers.get(cls.url, params={'s': query})).select('div.movie-poster')

        # i.select("a")[0].get('href').replace("kissanime","_anime") +"," + i.select("span")[0].get('data-id') )
        # ^ this will pass all data required directly to _scrape_episodes if you want to get rid of one or two get requests

        # The feature of passing links directly to anime-downloader makes passing data between functions convoluted
        # and creates a bunch un unnecessary get requests, because of this you gotta do at least 2 extra get requests
        # this also creates bugs when sitenames are similar
        search_results = [
            SearchResult(
                title=i.select("a > img")[0].get("alt"),
                url=i.select("a")[0].get('href').replace("kissanime", "_anime"))
            for i in search_results
        ]
        return search_results

    def _scrape_episodes(self):
        # This is retarded, you need to replace the url, otherwise it will go to the kissanime site because the links are similar
        _referer = self.url.replace("_anime", "kissanime")
        _id = helpers.soupify(helpers.get(_referer)).select("li.addto-later")[0].get("data-id")

        for i in range(1, 100):
            d = helpers.get("https://kissanimefree.net/load-list-episode/", params={"pstart": i, "id": _id, "ide": ""})
            if not d.text:  # MOVIES
                maxEp = 1
                break
            maxEp = int(helpers.soupify(d).select("li")[0].text)
            if not maxEp == i * 100:
                break
        return [f"{i},{_id},{_referer}" for i in range(1, maxEp + 1)]
        # you gotta know all three, the id of the episode, the id of the movie, and the referer

    def _scrape_metadata(self):
        realUrl = self.url.replace("_anime", "kissanime")
        soup = helpers.soupify(helpers.get(realUrl)).select('div.film > h1')
        self.title = soup[0].text


class AnimeFreeEpisode(AnimeEpisode, sitename='kissanimefree'):
    def _get_sources(self):
        ids = self.url.split(",")
        ep = ids[0]
        realId = int(ids[0]) + int(ids[1]) + 2
        _referer = ids[2]

        realUrl = helpers.post("https://kissanimefree.net/wp-admin/admin-ajax.php",
                               referer=f"https://kissanimefree.net/episode/{_referer}-episode-{realId}/",
                               data={"action": "kiss_player_ajax", "server": "vidcdn", "filmId": realId}).text

        realUrl = realUrl if realUrl.startswith('http') else "https:" + realUrl

        txt = helpers.get(realUrl).text
        # gets src="//vidstreaming.io/loadserver.php?id=MTIyNjM4&title=Naruto"></iframe>
        vidstream_regex = r'src=[^\s]*(((vidstreaming\.io)|(gogo-stream\.com))[^"\']*)'
        surl = re.search(vidstream_regex, txt)
        if surl:
            if surl.group(1):
                return [('vidstream', surl.group(1))]

        logger.debug('Failed vidstream text: {}'.format(txt))
        return ''

