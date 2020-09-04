from anime_downloader.downloader.base_downloader import BaseDownloader
from anime_downloader import session
from pySmartDL import SmartDL
from pathlib import Path
import time
import sys, os
# import subprocess

session = session.get_session()


class pySmartDL_Integrated(BaseDownloader):
    def _download(self):
        path = Path(self.path)
        headers = self.source.headers

        if 'user-agent' not in headers:
            headers['user-agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101Firefox/56.0"

        if self.source.referer:
            headers['Referer'] = self.source.referer

        url = self.source.stream_url
        request_args = {'headers': headers}

        dest = str(self.path) # str(path.parent.absolute())
        obj = SmartDL(url, dest, request_args=request_args, progress_bar=True)
        obj.start()
        time.sleep(1)
        sys.exit(0)