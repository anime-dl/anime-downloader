from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers

class AnimeOnline360(BaseExtractor):
    def _get_data(self):
        try:
            html = helpers.soupify(helpers.get(self.url))
            soup = html.find('li', class_='dooplay_player_option')
            anime_type = soup['data-type']
            anime_id = soup['data-post']
            referrer = helpers.get(f"https://animeonline360.me/wp-json/dooplayer/v1/post/{anime_id}?type={anime_type}&source=1").json()['embed_url']
            stream_url = referrer.split('?source=')[1].split('&')[0].replace('%2F', '/').replace('%3A', ':')
            return {
                'stream_url': stream_url,
                'referer': referrer
            }
        except:
        	return {"stream_url": ''}