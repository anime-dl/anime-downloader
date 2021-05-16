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

        headers = {"Referer": "https://kwik.cx/"}

        res = requests.get(self.url, headers=headers)

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
        nodeRes = str(subprocess.getoutput(f"node {tf}"))

        ld(nodeRes)

        stream_url = re.search(
            r"source='([^;]*)';", nodeRes).group().replace("source='", "").replace("';", "")

        ld(stream_url)

        return {
            'stream_url': stream_url,
            'referer': "https://kwik.cx/"
        }
