import re
from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
from anime_downloader import util
import logging

logger = logging.getLogger(__name__)

class Thirdparty(BaseExtractor):
    def _get_data(self):
        eval_regex = r'eval\(.*\)'
        file_regex = r"file('|\"|):*.'(http.*?),"
        soup = helpers.soupify(helpers.get(self.url))
        packed_js = r'{}'.format(re.search(eval_regex,str(soup)).group())
        logger.debug('Packed javascript: {}'.format(packed_js))
        js = util.deobfuscate_packed_js(packed_js)
        file = re.search(file_regex,js).group(2)
        return {'stream_url': file}
