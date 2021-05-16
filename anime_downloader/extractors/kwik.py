import logging
from platform import node
import re
import subprocess
import requests
import tempfile

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites.helpers.request import temp_dir
from anime_downloader.sites import helpers
from anime_downloader import util
from anime_downloader.util import eval_in_node
from subprocess import CalledProcessError

logger = logging.getLogger(__name__)


class Kwik(BaseExtractor):
    '''Extracts video url from kwik pages, Kwik has some `security`
       which allows to access kwik pages when only referred by something
       and the kwik video stream when referred through the corresponding
       kwik video page.
    '''

    def _get_data(self):
        ld = logger.debug
        # Kwik servers don't have direct link access you need to be referred
        # from somewhere, I will just use the url itself. We then
        # have to rebuild the url. Hopefully kwik doesn't block this too

        # Necessary
        # ld(self.url)
        #self.url = self.url.replace(".cx/e/", ".cx/f/")
        #self.headers.update({"referer": self.url})

        headers = {"Referer": "https://kwik.cx/"}

        res = requests.get(self.url, headers=headers)

        # ld(res.text)

        evalText = helpers.soupify(res.text)

        scripts = evalText.select("script")

        for i in scripts:
            rexd = re.compile("<script>eval[\s\S]*<\/script>").match(str(i))
            if not rexd == None:
                rexd = rexd.group()
                rexd = rexd.replace("<script>", "")
                rexd = rexd.replace("</script>", "")
                break

        tf = tempfile.mktemp(dir=temp_dir)

        with open(tf, 'w', encoding="utf-8") as f:
            f.write(rexd)

        # print(tf)

        # ld(nodeRes)

        nodeRes = str(subprocess.getoutput(f"node {tf}"))

        ld(nodeRes)

        stream_url = re.search(
            r"source='([^;]*)';", nodeRes).group().replace("source='", "").replace("';", "")
        #reg = re.compile("[\s\S]*")

        ld(stream_url)

        #kwik_text = resp.text

        #title_re = re.compile(r'title>(.*)<')
        #title = title_re.search(kwik_text).group(1)

        return {
            'stream_url': stream_url,
            # 'meta': {
            #   'title': title,
            #   'thumbnail': ''
            # },
            'referer': "https://kwik.cx/"
        }

        #cookies = util.get_hcaptcha_cookies(self.url)

        # if not cookies:
        #    resp = util.bypass_hcaptcha(self.url)
        # else:
        #    resp = requests.get(self.url, cookies=cookies)

        #
        #deobfuscated = None

        #loops = 0
        # while not deobfuscated and loops < 6:
        #    try:
        #        deobfuscated = helpers.soupify(util.deobfuscate_packed_js(re.search(r'<(script).*(var\s+_.*escape.*?)</\1>(?s)', kwik_text).group(2)))
        #    except (AttributeError, CalledProcessError) as e:
        #        if type(e) == AttributeError:
        #            resp = util.bypass_hcaptcha(self.url)
        #            kwik_text = resp.text

        #        if type(e) == CalledProcessError:
        #            resp = requests.get(self.url, cookies=cookies)
        #    finally:
        #        cookies = resp.cookies
        #
        #        loops += 1

        #post_url = deobfuscated.form["action"]
        #token = deobfuscated.input["value"]

        #resp = helpers.post(post_url, headers=self.headers, params={"_token": token}, cookies=cookies, allow_redirects=False)
        #stream_url = resp.headers["Location"]

        #logger.debug('Stream URL: %s' % stream_url)

        # return {
        #    'stream_url': stream_url,
        #    'meta': {
        #        'title': title,
        #        'thumbnail': ''
        #    },
        #    'referer': None
        # }
