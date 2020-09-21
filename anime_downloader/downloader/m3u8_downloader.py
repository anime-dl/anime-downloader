from anime_downloader.downloader.base_downloader import BaseDownloader
import time
import sys
import os
from anime_downloader.util import make_dir
import subprocess
import logging
import json

logger = logging.getLogger(__name__)


class m3u8(BaseDownloader):
    def _download(self):
        expected_file = os.path.abspath(self.path)
        cmd = f'm3u8-dl -r {self.source.referer} --insecure -t 16 {self.source.stream_url} {expected_file}'
        # As the m3u8 downloader only creates the mp4 file when complete just
        # checking that is exists is sufficent.
        if os.path.isfile(expected_file):
            logger.info(f'{expected_file} already downloaded.')
            return

        # m3u8_dl doesn't make the directories itself, hence why this needs to be done.
        file_dir = '/'.join(expected_file.split('/')[:-1])
        make_dir(file_dir)

        # Checks if it can resume.
        if os.path.isfile(os.getcwd() + '/m3u8_dl.restore'):
            with open(os.getcwd() + '/m3u8_dl.restore') as f:
                # Checks if the file downloaded is the same as expected.
                # Without this it'll resume the previous download regardless
                # of what the user chooses does.
                restore_json = json.load(f)
                # Be aware that '.mp4' here needs to be changed if cmd_dict is changed.
                if restore_json['user_options'].get('output_file') == expected_file:
                    # Only restores if it can AND the expected file location is the same.
                    # NOTE: only the most recent download can be resumed!
                    cmd = cmd + ' --restore'

        p = subprocess.Popen(cmd.split(' '))
        return_code = p.wait()

        if return_code != 0:
            # Sleep for a while to make sure downloader exits correctly
            time.sleep(2)
            sys.exit(1)
