from anime_downloader.downloader.base_downloader import BaseDownloader
from anime_downloader.util import download_m3u8
import os


class m3u8(BaseDownloader):
    def _download(self):
        expected_file = os.path.abspath(self.path)
        download_m3u8(self.source.stream_url, self.source.referer, expected_file)
