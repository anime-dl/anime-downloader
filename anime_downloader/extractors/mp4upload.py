import logging
import re

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
from anime_downloader import util

logger = logging.getLogger(__name__)

class MP4Upload(BaseExtractor):
    def _get_data(self):
        soup = str(helpers.get(self.url).text)
        if 'File was deleted' in soup:
            logger.warning('File not found (Most likely deleted)')
            return {'stream_url':''}

        regex = r"eval\(function[\W\w]*?</script>"
        script = re.search(regex,soup).group().replace('</script>','')
        script = util.deobfuscate_packed_js(script)
        url = ''
        if re.search(r'player\.src\("([^"]*)',script):
            url = re.search(r'player\.src\("([^"]*)',script).group(1)
        elif re.search(r'src:"([^"]*)',script):
            url = re.search(r'src:"([^"]*)',script).group(1)
        return {
            'stream_url': url,
            'referer': self.url
        }
