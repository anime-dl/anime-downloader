import logging
import re
import requests

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
from anime_downloader import util
from subprocess import CalledProcessError

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
        self.headers.update({"referer": self.url})

        cookies = util.get_hcaptcha_cookies(self.url)

        if not cookies:
            resp = util.bypass_hcaptcha(self.url)
        else:
            resp = requests.get(self.url, cookies = cookies)

        title_re = re.compile(r'title>(.*)<')

        kwik_text = resp.text
        deobfuscated = None

        loops = 0
        while not deobfuscated and loops < 6:
            try:
                deobfuscated = helpers.soupify(util.deobfuscate_packed_js(re.search(r'<(script).*(var\s+_.*escape.*?)</\1>(?s)', kwik_text).group(2)))
            except (AttributeError, CalledProcessError) as e:
                if type(e) == AttributeError:
                    resp = util.bypass_hcaptcha(self.url)
                    kwik_text = resp.text

                if type(e) == CalledProcessError:
                    resp = requests.get(self.url, cookies = cookies)
            finally:
                cookies = resp.cookies
                title = title_re.search(kwik_text).group(1)
                loops += 1



        post_url = deobfuscated.form["action"]
        token = deobfuscated.input["value"]

        resp = helpers.post(post_url, headers = self.headers, params={"_token": token}, cookies = cookies, allow_redirects = False)
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
