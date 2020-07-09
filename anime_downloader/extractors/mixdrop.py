import re
from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
from anime_downloader import util
import logging

logger = logging.getLogger(__name__)

class Mixdrop(BaseExtractor):
    def _get_data(self):
        eval_regex = r'eval\(.*\)'
        wurl_regex = r'wurl.*?=.*?"(.*?)";'
        soup = helpers.get(self.url).text
        deobfuscated_js = util.deobfuscate_packed_js(re.search(eval_regex,soup).group())
        logger.debug('Deobfuscated JS: {}'.format(deobfuscated_js))
        url = re.search(wurl_regex,deobfuscated_js).group(1)
        logger.debug('Url: {}'.format(url))
        url = f'https:{url}' if url.startswith('//') else url
        return {'stream_url': url}
