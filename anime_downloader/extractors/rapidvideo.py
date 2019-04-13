import logging
import re
from bs4 import BeautifulSoup

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader import session

session = session.get_session()


class RapidVideo(BaseExtractor):
    def _get_data(self):
        url = self.url + '&q=' + self.quality
        logging.debug('Calling Rapid url: {}'.format(url))
        headers = self.headers
        headers['referer'] = url
        try:
            r = session.get(url, headers=headers)
            # This is a fix for new rapidvideo logic
            # It will return OK for a get request
            # even if there is a click button
            # This will make sure a source link is present
            soup = BeautifulSoup(r.text, 'html.parser')
            get_source(soup)
        except:
            r = session.post(url, {
                'confirm.x': 12,
                'confirm.y': 12,
                'block': 1,
            }, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')

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
            logging.debug(e)
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
