import logging
import re

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
from anime_downloader import util

logger = logging.getLogger(__name__)


class Kwik(BaseExtractor):
    '''Extracts video url from kwik pages, Kwik has some `security`
       which allows to access kwik pages when only refered by something
       and the kwik video stream when refered through the corresponding
       kwik video page.
    '''

    def _get_data(self):
        # Kwik servers don't have direct link access you need to be referred
        # from somewhere, I will just use the url itself. We then
        # have to rebuild the url. Hopefully kwik doesn't block this too
        eval_re = re.compile(r';(eval.*\))')
        stream_parts_re = re.compile(r'https:\/\/(.*?)\..*\/(\d+)\/(.*)\/.*token=(.*)&expires=([^\']+)')
        title_re = re.compile(r'title>(.*)<')

        kwik_text = helpers.get(self.url, referer=self.url).text
        obsfucated_js = eval_re.search(kwik_text).group(1)
        deobsfucated_js = util.deobfuscate_packed_js(obsfucated_js)

        title = title_re.search(kwik_text).group(1)
        cdn, digits, file, token, expires = stream_parts_re.search(deobsfucated_js).group(1, 2, 3, 4, 5)
        stream_url = f'https://{cdn}.nextstream.org/get/{token}/{expires}/mp4/{digits}/{file}/{title}'

        logger.debug('Stream URL: %s' % stream_url)
        return {
            'stream_url': stream_url,
            'meta': {
                'title': title,
                'thumbnail': ''
            },
            'referer': None
        }
