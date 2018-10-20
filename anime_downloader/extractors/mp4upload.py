import logging
import re
from bs4 import BeautifulSoup

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader import session

session = session.get_session()


class MP4Upload(BaseExtractor):
    '''Extracts video url from mp4upload embed pages, performs a request
    back to the non-embed mp4upload page to extract the title of the video
    albeit imperfectly as mp4upload doesn't place full title on the main
    page of whichever video you are dealing with.
    '''
    def _get_data(self):
        # Extract the important bits from the embed page, with thanks to the
        # code I saw from github user py7hon in his/her mp4upload-direct
        # program as inspiration for this. Only with regex.
        source_parts_re = re.compile(
                                r'.*?100\|(.*?)\|.*?\|video\|(.*?)\|(\d+)\|.*?',
                                re.DOTALL)

        mp4u_embed = session.get(self.url).text
        domain, video_id, protocol = source_parts_re.match(mp4u_embed).groups()

        logging.debug('Domain: %s, Video ID: %s, Protocol: %s' %
                      (domain, video_id, protocol))

        url = self.url.replace('embed-', '')
        # Return to non-embed page to collect title
        mp4u_page = BeautifulSoup(session.get(url).text, 'html.parser')

        title = mp4u_page.find('span', {'class': 'dfilename'}).text
        title = title[:title.rfind('_')][:title.rfind('.')].replace(' ', '_')

        logging.debug('Title is %s' % title)

        # Create the stream url
        stream_url = 'https://{}.mp4upload.com:{}/d/{}/{}.mp4'
        stream_url = stream_url.format(domain, protocol, video_id, title)

        logging.debug('Stream URL: %s' % stream_url)

        return {
            'stream_url': stream_url,
            'meta': {
                'title': title,
                'thumbnail': ''
            }
        }
