import logging
import re
import requests

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
        eval_re = re.compile(r';(eval.*\))')
        stream_parts_re = re.compile(r'https:\/\/(.*?)\..*\/(\d+)\/(.*)\/.*token=(.*)&expires=([^\']+)')
        title_re = re.compile(r'title>(.*)<')

        session = requests.Session()
        kwik_text = session.get(self.url, headers={"referer": self.url}).text

        title = title_re.search(kwik_text).group(1)
        kwik_text = helpers.soupify(kwik_text)
        deobfuscated = helpers.soupify(util.deobfuscate_packed_js([x for x in kwik_text.select("script") if 'escape' in x.text][0].text))

        helpers.get(self.url, referer=self.url)
        post_url = deobfuscated.form["action"]
        token = deobfuscated.input["value"]

        resp = session.post(post_url, headers={"referer": self.url}, params={"_token": token}, allow_redirects = False)
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
