import logging
import re
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)

class Anime8(Anime, sitename = 'anime8'):
    sitename = 'anime8'

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(helpers.get('https://anime8.ru/Search/', params={'s': query}).text)
        results = soup.select('div.ml-item > a')

        search_results = [
            SearchResult(
                title = i.find('h2').text,
                url = i['href'],
                meta_info = {
                    'version_key_subbed':'(Sub)',
                    'version_key_dubbed':'(Dub)'
                })
            for i in results
            ]
        return search_results


    def _scrape_episodes(self):
        link = helpers.soupify(helpers.get(self.url).text).select_one('div#mv-info > a')['href']
        soup = helpers.soupify(helpers.get(link).text)
        eps = soup.select('a[class*="btn-eps first-ep last-ep"]')
        eps = [x.get('href') for x in eps]
        count = range(len(eps) - 1)
        for a, b in zip(eps, count):
            if '-Preview' in a:
                eps.pop(b)
        return eps


    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.select('div.thumb.mvic-thumb > img')[0]['alt']


class Anime8Episode(AnimeEpisode, sitename='anime8'):
    def _get_sources(self):
        resp = helpers.get(self.url)
        # Gets the ctk and id from the page used for a post request.
        ctk = re.search(r"ctk\s+=\s+'(.*)?';", resp.text).group(1)
        _id = re.search(r"episode_id\s*=\s*([^;]*)", resp.text).group(1)

        logger.info('ctk: {}'.format(ctk))
        logger.info('id: {}'.format(_id))

        # The post request returns an embed. 
        resp = helpers.post("https://anime8.ru/ajax/anime/load_episodes_v2?s=fserver", data = {"episode_id": _id, "ctk": ctk})
        # Gets the real embed url. Json could be used on the post request, but this is probably more reliable.
        embed = re.search(r"iframe\s*src.*?\"([^\"]*)", resp.text).group(1).replace('\\','')

        return [('streamx', embed)]