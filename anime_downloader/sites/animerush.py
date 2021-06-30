from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from anime_downloader.extractors.init import ALL_EXTRACTORS

import logging
import re

logger = logging.getLogger(__name__)


class AnimeRush(Anime, sitename='animerush'):
    sitename = 'animerush'
    url = f'https://www.{sitename}.tv/search.php'

    @classmethod
    def search(cls, query):
        search_results = helpers.soupify(helpers.get(cls.url, params={'searchquery': query}))
        title = search_results.select('h3')  # Stored in another place
        results = search_results.select('a.highlightit')
        return [
            SearchResult(
                title=title[i].text,
                url='https:' + results[i].get('href'))
            for i in range(1, len(results))]

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url)).select('div.episode_list > a')
        return ['https:' + i.get('href') for i in soup[::-1] if "Coming soon" not in str(i)]

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.select('div.amin_week_box_up1 > h1')[0].text


class AnimeRushEpisode(AnimeEpisode, sitename='animerush'):
    def _get_sources(self):
        soup = helpers.soupify(helpers.get(self.url))
        sources = ([[self._get_url('https:' + i.get('href')), i.text] for i in soup.select('div.episode_mirrors > div > h3 > a')])
        sources.append([self._get_url(self.url), soup.select('iframe')[-1].get('title')])

        logger.debug('Sources: {}'.format(sources))

        sources_list = []
        # Sources [0] is the url [1] is the name of the source
        # eg: [['https://mp4upload.com/embed-r07potgdvbkr-650x370.html', 'Mp4upload Video']]
        domain_regex = r"\/\/(?:\w{3,6}\.)?(.*?)\."
        for i in sources:
            found = False
            domain = re.findall(domain_regex, i[0])[0].lower()

            for extractor in ALL_EXTRACTORS:
                if re.match(extractor['regex'], domain):
                    found = True

            if not found:
                continue

            sources_list.append({
                'extractor': domain,
                'url': i[0],
                'server': i[1],
                'version': 'subbed'
            })

        return self.sort_sources(sources_list)

    def _get_url(self, url):  # The links are hidden on other pages
        soup = helpers.soupify(helpers.get(url))
        return (soup.select('iframe')[-1].get('src'))
