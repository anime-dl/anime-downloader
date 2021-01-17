from anime_downloader.extractors.base_extractor import BaseExtractor


class Twist(BaseExtractor):
    def _get_data(self):
        return {
            'stream_url': self.url,
            'referer': "https://twist.moe" }