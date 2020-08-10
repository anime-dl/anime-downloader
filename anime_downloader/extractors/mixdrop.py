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
        # Group 2 is url
        # Allows redirects
        redirect_regex = r"\s*window\.location\s*=\s*('|\")(.*?)('|\")"
        # allow_redirects=True doesn't seem to be working
        soup = helpers.get(self.url, allow_redirects=True).text
        redirect = re.search(redirect_regex,soup)

        if redirect:
            url = 'https://mixdrop.to' + redirect.group(2)
            soup = helpers.get(url).text

        if 'WE ARE SORRY' in soup:
            return ''

        deobfuscated_js = util.deobfuscate_packed_js(re.search(eval_regex,soup).group())
        logger.debug('Deobfuscated JS: {}'.format(deobfuscated_js))
        url = re.search(wurl_regex,deobfuscated_js).group(1)
        logger.debug('Url: {}'.format(url))
        url = f'https:{url}' if url.startswith('//') else url
        return {'stream_url': url}
