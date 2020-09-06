import re
from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
import logging

logger = logging.getLogger(__name__)


class Ezlink(BaseExtractor):
    def _get_data(self):
        referer = 'https://topmoviesonline.org/'
        main = helpers.get(self.url, referer=referer).text
        # Matches GetVideoSource('      redirector.php?link1=NxN    ',">HLS      Server Main     </li>
        source_regex = r"('|\")(redirector\.php[^'\"]*).*?(Server Main|Plyr\.xyz).*?</li"
        sources = re.findall(source_regex, main)
        if sources:
            for i in sources:
                if 'Plyr.xyz' in i[2]:
                    source = helpers.get('https://player.ezylink.co/' + i[1], referer=referer).text
                    quality_regex = r'"label":\s*?"' + self.quality.upper() + r'"[\W\w]*"file":\s*?"(http[^"]*?)"'
                    # Matches

                    # "label": "1080P",
                    # "file": "https://plyr.xyz/"

                    # Provided the quality is 1080p
                    match = re.search(quality_regex, source)
                    if match:
                        return {'stream_url': match.group(1)}

                if 'Server Main' in i[2] and self.quality == '360p':
                    source = helpers.get('https://player.ezylink.co/' + i[1], referer=referer).text
                    file = get_file(source)
                    return {'stream_url': file}
        else:
            file = get_file(main)
            return {'stream_url': file}

        return {'stream_url': ''}


def get_file(html):
    file_regex = r'"file":"(http[^"]*?)"'
    file = re.search(file_regex, html)
    if file:
        file = file.group(1).replace('\\', '')
    else:
        file = ''

    return file
