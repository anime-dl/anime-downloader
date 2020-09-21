from anime_downloader.downloader.base_downloader import BaseDownloader
from anime_downloader.util import get_m3u8_command
import time
import sys
import os
import subprocess


class m3u8(BaseDownloader):
    def _download(self):
        expected_file = os.path.abspath(self.path)
        cmd = f'm3u8-dl -r {self.source.referer} --insecure -t 16 {self.source.stream_url} {expected_file}'
        cmd = get_m3u8_command(cmd, expected_file)
        if cmd:
            p = subprocess.Popen(cmd.split(' '))
            return_code = p.wait()

            if return_code != 0:
                # Sleep for a while to make sure downloader exits correctly
                time.sleep(2)
                sys.exit(1)
