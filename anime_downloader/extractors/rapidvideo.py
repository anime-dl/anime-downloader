import logging
import re

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)


class RapidVideo(BaseExtractor):
    def _get_data(self):
        url = self.url + '&q=' + self.quality
        logger.debug('Calling Rapid url: {}'.format(url))
        headers = self.headers
        headers['referer'] = url

        try:
            r = helpers.get(url, headers=headers)
            soup = helpers.soupify(r)
            stream_url = get_source(soup)
        except Exception as e:
            logger.debug('Exception happened when getting normally')
            logger.debug(e)
            r = helpers.post(url, data={
                'confirm.x': 12,
                'confirm.y': 12,
                'block': 1,
            }, headers=headers)
        soup = helpers.soupify(r)

        # TODO: Make these a different function. Can be reused in other classes
        #       too
        title_re = re.compile(r'"og:title" content="(.*)"')
        image_re = re.compile(r'"og:image" content="(.*)"')

        try:
            stream_url = get_source(soup)
        except IndexError:
            stream_url = None

        try:
            title = str(title_re.findall(r.text)[0])
            thumbnail = str(image_re.findall(r.text)[0])
        except Exception as e:
            title = ''
            thumbnail = ''
            logger.debug(e)
            pass

        return {
            'stream_url': stream_url,
            'meta': {
                'title': title,
                'thumbnail': thumbnail,
            },
        }


def get_source(soup):
    src_re = re.compile(r'src: "(.*)"')
    try:
        return soup.find_all('source')[0].get('src')
    except IndexError:
        return str(src_re.findall(str(soup))[0])
