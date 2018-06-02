from anime_downloader.sites.kissanime import Kissanime, KissanimeEpisode
from bs4 import BeautifulSoup
from anime_downloader.sites.exceptions import NotFoundError


class KissasianEpisode(KissanimeEpisode):
    _base_url = ''
    VERIFY_HUMAN = False

    # def _scrape_episode(self, reponse):
    #     soup = BeautifulSoup(reponse.text, 'html.parser')
    #     data = dict()
    #     data['stream_url'] = soup.find_all('iframe')
    #     data['title'] = ''
    #     data['image'] = ''
    #     return data


class Kissasian(Kissanime):
    sitename = 'kisscartoon'
    _episodeClass = KissasianEpisode

    def _getEpisodeUrls(self, soup):
        ret = soup.find('div', {'class': 'listing'}).find_all('a')
        ret = [str(a['href']) for a in ret]

        if ret == []:
            err = 'No episodes found in url "{}"'.format(self.url)
            args = [self.url]
            raise NotFoundError(err, *args)

        return list(reversed(ret))
