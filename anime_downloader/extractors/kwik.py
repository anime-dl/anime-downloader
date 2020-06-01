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

        #Necessary
        self.url = self.url.replace(".cx/e/", ".cx/f/")

        title_re = re.compile(r'title>(.*)<')

        resp = helpers.get(self.url, headers={"referer": self.url})
        kwik_text = resp.text
        cookies = resp.cookies

        title = title_re.search(kwik_text).group(1)
        deobfuscated = helpers.soupify((util.deobfuscate_packed_js(re.search(r'<(script).*(var\s+_.*escape.*?)</\1>(?s)', kwik_text).group(2))))

        post_url = deobfuscated.form["action"]
        token = deobfuscated.input["value"]

        resp = helpers.post(post_url, headers={"referer": self.url}, params={"_token": token}, cookies=cookies, allow_redirects = False)
        stream_url = resp.headers["Location"]

        logger.debug('Stream URL: %s' % stream_url)
        return {
            'stream_url': stream_url,
            'meta': {
                'title': title,
                'thumbnail': ''
            },
            'referer': None
        }
