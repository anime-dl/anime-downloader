import re

from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers


class Trollvid(BaseExtractor):
    def _get_data(self):
        # TODO: Provide referer by source
        referer = 'https://anistream.xyz'

        req = helpers.get(self.url, referer=referer)
        source_regex = r'<source src="(.*?)"'
        source = re.search(source_regex, req.text)

        # Matches: token="eyJ0eXA"
        token_regex = r"token\s*=\s*['\"|']([^\"']*)"
        token = re.search(token_regex, req.text)

        if source:
            return {
                'stream_url': source.group()
            }

        elif token:
            token = token.group(1)
            trollvid_id = self.url.split('/')[-1]  # something like: 084df78d215a
            post = helpers.post(f'https://mp4.sh/v/{trollvid_id}',
                                data={'token': token},
                                referer=self.url,
                                ).json()

            # {'success':True} on success.
            if post.get('success') and post.get('data'):
                return {
                    'stream_url': post['data']
                }

        # In case neither methods work.
        return {'stream_url': ''}
