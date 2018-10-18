import re
import base64

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader import session


class StreamMoe(BaseExtractor):
    def _get_data(self):
        url = self.url
        res = session.get_session().get(url)
        content_re = re.compile(r"= atob\('(.*?)'\)")
        source_re = re.compile(r'source src="(.*?)"')

        enc_cont = content_re.findall(res.text)[0]
        content = base64.b64decode(enc_cont).decode('utf-8')

        stream_url = source_re.findall(content)[0]

        return {
            'stream_url': stream_url,
            'meta': {
                'title': '',
                'thumbnail': '',
            }
        }
