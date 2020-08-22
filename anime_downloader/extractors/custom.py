from anime_downloader.extractors.base_extractor import BaseExtractor


class Custom(BaseExtractor):
    def _get_data(self):
        return {
            'stream_url': self.url.split('\n')[0],
            'referer': self.url.split('\n')[1]
        }
