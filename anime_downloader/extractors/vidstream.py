import logging
import re

from anime_downloader.config import Config
from anime_downloader.extractors.base_extractor import BaseExtractor
import anime_downloader.extractors as extractors
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)

class VidStream(BaseExtractor):
    def _get_data(self):
        """
        Config:
        List of servers. Will use servers in order. 
        For example: ["hydrax","vidstream"] will prioritize the HydraX link.
        Available servers: links (below) and vidstream
        """

        links = {
        "gcloud":"https://gcloud.live/",
        "mp4upload":"https://www.mp4upload.com/",
        "cloud9":"https://cloud9.to",
        "hydrax":"https://hydrax.net",
        "mixdrop":"https://mixdrop.co"
        }

        url = self.url.replace('https:////','https://')
        url = url.replace('https://vidstreaming.io/download','https://vidstreaming.io/server.php')
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
                if j.get('data-video').startswith(links.get(i,'None')):
                    """
                    Another class needs to get created instead of using self, not to impact future loops.
                    If the extractor fails it will rerun, which would lead to an error if self was changed 
                    """
                    info = self.__dict__.copy()
                    info['url'] = j.get('data-video')
                    _self = Extractor(info)
                    """Gives away the link to another extractor"""
                    return extractors.get_extractor(i)._get_data(_self)


    def _get_link(self,soup):
        """
        Matches something like
        f("MTE2MDIw&title=Yakusoku+no+Neverland");
        """
        sources_regex = r'>\s*?f\("(.*?)"\);'
        sources_url = re.search(sources_regex,str(soup)).group(1)
        sources_json = helpers.get(f'https://vidstreaming.io/ajax.php?id={sources_url}', referer=self.url).json()

        logger.debug('Sources json: {}'.format(str(sources_json)))
        """
        Maps config vidstreaming sources to json results.
        When adding config in the future make sure "vidstream"
        is in the name in order to pass the check above.
        """
        sources_keys = {
            "vidstream":"source",
            "vidstream_bk":"source_bk"
        }

        """
        Elaborate if statements to get sources_json["source"][0]["file"]
        based on order in config.
        """

        servers = Config._read_config()['siteconfig']['vidstream']['servers']
        print(sources_json["source"][0]["file"])
        for i in servers:
            if i in sources_keys:
                if sources_keys[i] in sources_json:
                    if 'file' in sources_json[sources_keys[i]][0]:
                        return {
                            'stream_url': sources_json[sources_keys[i]][0]['file'],
                            'referer': self.url
                        }

        return {'stream_url':''}


"""dummy class to prevent changing self"""
class Extractor: 
    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)
