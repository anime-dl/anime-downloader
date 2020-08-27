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
        script = script + "player.source.sources[0].src;"
        sandbox = """{
            player: {},
            document: { getElementById: x => x },
            $: () => ({ ready: x => x })
        }"""
        url = util.eval_in_node(script, sandbox=sandbox)
        return {
            'stream_url': url,
            'referer': self.url
        }
