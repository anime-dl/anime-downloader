import logging
import re

from anime_downloader.config import Config
from anime_downloader.extractors.base_extractor import BaseExtractor
import anime_downloader.extractors as extractors
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)


class VidStream(BaseExtractor):
    # NOTE! website renamed from vidstreaming.io to gogo-stream.com
    def _get_data(self):
        """
        Config:
        List of servers. Will use servers in order.
        For example: ["hydrax","vidstream"] will prioritize the HydraX link.
        Available servers: links (below) and vidstream
        """

        links = {
            "gcloud": "https://gcloud.live/",
            "mp4upload": "https://www.mp4upload.com/",
            "cloud9": "https://cloud9.to",
            "hydrax": "https://hydrax.net",
            "mixdrop": "https://mixdrop.co"
        }

        url = self.url.replace('https:////', 'https://')
        url = url.replace('https://gogo-stream.com/download',
                          'https://gogo-stream.com/server.php')
        soup = helpers.soupify(helpers.get(url))
        linkserver = soup.select('li.linkserver')
        logger.debug('Linkserver: {}'.format(linkserver))

        """Dirty, but self.config isn't supported for extractors."""
        servers = Config._read_config()['siteconfig']['vidstream']['servers']

        for i in servers:
            """
            Will only use _get_link() if the site is actually the real vidstream, as clones
            use a different layout for their own videos
            """
            if 'vidstream' in i and 'vidstream' in self.url:
                return self._get_link(soup)
            for j in linkserver:
                if j.get('data-video').startswith(links.get(i, 'None')):
                    """
                    Another class needs to get created instead of using self, not to impact future loops.
                    If the extractor fails it will rerun, which would lead to an error if self was changed
                    """
                    info = self.__dict__.copy()
                    info['url'] = j.get('data-video')
                    _self = Extractor(info)
                    """Gives away the link to another extractor"""
                    return extractors.get_extractor(i)._get_data(_self)

        return {'stream_url': ''}

    def _get_link(self, soup):

        # Gets:
        # <input type="hidden" id="id" value="MTEyMzg1">
        # <input type="hidden" id="title" value="Yakusoku+no+Neverland">
        # <input type="hidden" id="typesub" value="SUB">
        # Used to create a download url.
        try:
            soup_id = soup.select('input#id')[0]['value']
        except IndexError:
            return self._get_link_new(soup)

        soup_title = soup.select('input#title')[0]['value']
        soup_typesub = soup.select('input#typesub')[0].get('value', 'SUB')

        sources_json = helpers.get(f'https://gogo-stream.com/ajax.php', params={
            'id': soup_id,
            'typesub': soup_typesub,
            'title': soup_title,
        }, referer=self.url).json()

        logger.debug('Sources json: {}'.format(str(sources_json)))
        """
        Maps config vidstreaming sources to json results.
        When adding config in the future make sure "vidstream"
        is in the name in order to pass the check above.
        """
        sources_keys = {
            "vidstream": "source",
            "vidstream_bk": "source_bk"
        }

        """
        Elaborate if statements to get sources_json["source"][0]["file"]
        based on order in config.
        """

        servers = Config._read_config()['siteconfig']['vidstream']['servers']

        for i in servers:
            if i in sources_keys:
                if sources_keys[i] in sources_json:
                    if 'file' in sources_json[sources_keys[i]][0]:
                        return {
                            'stream_url': sources_json[sources_keys[i]][0]['file'],
                            'referer': self.url
                        }

        return {'stream_url': ''}

    def _get_link_new(self, soup):
        link_buttons = soup.select('div.mirror_link')[
            0].select('div.dowload > a[href]')
        return {'stream_url': link_buttons[0].get('href')}


class Extractor:
    """dummy class to prevent changing self"""

    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)
