from anime_downloader.downloader.base_downloader import BaseDownloader
from pySmartDL import SmartDL
from pathlib import Path
import time
import sys
import os


class pySmartDL(BaseDownloader):
    def _download(self):
        path = Path(self.path)
        headers = self.source.headers

        if 'user-agent' not in headers:
            headers['user-agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101Firefox/56.0"

        # This allows backwards compatible while also working with
        # PySmartDl as it only passes user agent if spelled "User-Agent"
        headers['User-Agent'] = headers.pop('user-agent')

        if self.source.referer:
            headers['Referer'] = self.source.referer

        url = self.source.stream_url
        request_args = {'headers': headers}

        dest = str(self.path)  # str(path.parent.absolute())
        obj = SmartDL(url, dest, request_args=request_args, progress_bar=True, verify=False)
        obj.start()
