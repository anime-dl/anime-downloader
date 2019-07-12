from anime_downloader.downloader.base_downloader import BaseDownloader
from anime_downloader import session

from pathlib import Path
import time
import sys
import subprocess

session = session.get_session()


class ExternalDownloader(BaseDownloader):
    def _download(self):
        executable = self.options['executable']
        opts = self.options['cmd_opts']
        path = Path(self.path)

        # TODO: Pull this into downloadersession?
        rep_dict = {
            'stream_url': self.url,
            'file_format': str(path.name),
            'download_dir': str(path.parent.absolute()),
            'referer': self.referer,
        }

        cmd = [executable] + opts
        cmd = [c.format(**rep_dict) for c in cmd]
        p = subprocess.Popen(cmd)
        return_code = p.wait()

        if return_code != 0:
            # Sleep for a while to make sure downloader exits correctly
            time.sleep(2)
            sys.exit(1)
