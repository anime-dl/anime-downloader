import logging
import re
from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)


class Kwik(BaseExtractor):
    '''Extracts video url from kwik pages, Kwik has some `security`
       which allows to access kwik pages when only refered by something
       and the kwik video stream when refered through the corresponding
       kwik video page.
    '''

    def _get_data(self):

        # Need a javascript deobsufication api/python, so someone smarter
        # than me can work on that for now I will add the pattern I observed

        # alternatively you can pattern match on `src` for stream_url part
        source_parts_re = re.compile(r'action=\"([^"]+)\".*value=\"([^"]+)\".*Click Here to Download',
                                     re.DOTALL)

        # Kwik servers don't have direct link access you need to be referred
        # from somewhere, I will just use the url itself.

        download_url = self.url.replace('kwik.cx/e/', 'kwik.cx/f/')

        kwik_text = helpers.get(download_url, referer=download_url).text
        post_url, token = source_parts_re.search(kwik_text).group(1, 2)

        stream_url = helpers.post(post_url,
                                  referer=download_url,
                                  data={'_token': token},
                                  allow_redirects=False).headers['Location']

        title = stream_url.rsplit('/', 1)[-1].rsplit('.', 1)[0]

        logger.debug('Stream URL: %s' % stream_url)
        return {
            'stream_url': stream_url,
            'meta': {
                'title': title,
                'thumbnail': ''
            },
            'referer': None
        }
