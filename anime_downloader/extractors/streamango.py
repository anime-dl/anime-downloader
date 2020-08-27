import logging
import re
import subprocess

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
from anime_downloader.util import eval_in_node


logger = logging.getLogger(__name__)


class Streamango(BaseExtractor):
    def _get_data(self):
        url = self.url

        res = helpers.get(url)
        js = re.findall(
            r'<script type="text/javascript">([^"]+)var srces', res.text)[0]
        src = re.findall(
            r'src:d\(([^"]+?)\)', res.text)[0]
        js = "window = {}; \n" + js + f"console.log(window.d({src}))"
        logger.debug(f"Evaling: {js}")
        output = eval_in_node(js)
        stream = "https:" + output
        return {
            'stream_url': stream,
        }
