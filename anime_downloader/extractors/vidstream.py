from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.config import Config
from anime_downloader.sites import helpers
import logging
import re
import json

logger = logging.getLogger(__name__)


class VidStream(BaseExtractor):
    def _get_data(self):
        id_ = re.search(r'id\=(.*?)[&]', url)[1]
        url = f'https://gogo-play.net/ajax.php?id={id_}'

        data = helpers.get(url).json()
        links = [data['source'][0]['file'], data['source_bk'][0]['file']]
        servers = Config._read_config()['siteconfig']['vidstream']['servers']
        if servers[0] == "vidstream":
            return {
                'stream_url': links[0]
            }
        elif servers[0] == "vidstream_bk":
            return {
                'stream_url': links[1]
            }
