from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
import re
import json


class Anistream(Anime, sitename='anistream.xyz'):
    """
    Site: http://anistream.xyz

    Config
    ------
    version: One of ['subbed', 'dubbed]
        Selects the version of audio of anime.
    """
    sitename = 'anistream.xyz'
    QUALITIES = ['360p', '480p', '720p', '1080p']

    @classmethod
    def search(self, query):
        soup = helpers.soupify(helpers.get(f"https://anistream.xyz/search?term={query}"))
        results = soup.select_one('.card-body').select('a')
        results = [
            SearchResult(title=v.text, url=v.attrs['href'])
            for v in results
        ]
        return results

    def _scrape_episodes(self):
        version = self.config.get('version', 'subbed')
        soup = helpers.soupify(helpers.get(self.url))
        versions = soup.select_one('.card-body').select('ul')
        def get_links(version):
            links = [v.attrs['href'] for v in version.select('a')][::-1]
            return links
        dubbed = get_links(versions[1])
        subbed = get_links(versions[0])
        # TODO: This should be handled more gracefully
        # revist once config API is finalized
        if version.lower() == 'dubbed':
            choice = dubbed
            other = subbed
        else:
            choice = subbed
            other = dubbed
        if choice:
            return choice
        # TODO: warn about choice not available
        return other

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url))
        self.title = soup.select_one('.card-header > h1').text


class AnistreamEpisode(AnimeEpisode, sitename='anistream.xyz'):
    def _get_sources(self):
        ep = re.findall('episode = (.*);', helpers.get(self.url).text)[0]
        ep = json.loads(ep)
        videos = ep['videos']
        sources = []
        for v in videos:
            if v['host'] == 'trollvid':
                sources.append(('trollvid', 'https://trollvid.net/embed/' + v['id']))
            if v['host'] == 'mp4upload':
                sources.append(('mp4upload', f'https://www.mp4upload.com/embed-{v["id"]}.html'))
        return sorted(sources)
