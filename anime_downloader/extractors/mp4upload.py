import logging
import re

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers

logger = logging.getLogger(__name__)


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
        source_parts_re = re.compile(r'.*?false\|(.*?)\|.*?\|video\|(.*?)\|(\d+)\|.*?', re.DOTALL)
        not_download_page_re = re.compile(r'type="submit" name="method_free"', re.DOTALL)
        title_re = re.compile(r'h2>Download File (.*?)\.mp4<\/h2>', re.DOTALL)

        mp4u_embed = helpers.get(self.url).text
        source_parts = source_parts_re.match(mp4u_embed)
        if not source_parts:
            raise Exception(f"Failed to find source parts to build URL {self.url}")

        domain, video_id, protocol = source_parts.groups()

        logger.debug('Domain: %s, Video ID: %s, Protocol: %s' % (domain, video_id, protocol))

        url = self.url.replace('embed-', '')
        # Return to non-embed page to collect title
        mp4u_page = helpers.get(url, referer=self.url).text
        title = title_re.search(mp4u_page)
        # The N/A here will probably come to haunt me some day
        title = title.groups()[0] if title else 'N/A'

        logger.debug('Title is %s' % title)

        # Create the stream url
        stream_url = 'https://{}.mp4upload.com:{}/d/{}/{}.mp4'
        stream_url = stream_url.format(domain, protocol, video_id, title)

        logger.debug('Stream URL: %s' % stream_url)

        return {
            'stream_url': stream_url,
            'meta': {
                'title': title,
                'thumbnail': ''
            }
        }
