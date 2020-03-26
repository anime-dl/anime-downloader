import logging
import re

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
from anime_downloader import util

logger = logging.getLogger(__name__)

class MP4Upload(BaseExtractor):
    def _get_data(self):
        soup = str(helpers.get(self.url).text)
        regex = r"eval\(function[\W\w]*?</script>"
        script = re.search(regex,soup).group().replace('</script>','')
        script = util.deobfuscate_packed_js(script)
        url = re.search(r'player\.src\("[^"]*',script).group().replace('player.src("','')
        return {
            'stream_url': url,
            'referer': self.url
        }
