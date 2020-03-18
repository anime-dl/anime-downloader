from anime_downloader.extractors.base_extractor import BaseExtractor


class AnimeVideo(BaseExtractor):
    def _get_data(self):
        return {
            'stream_url': self.url,
            'referer': self.url
        }
