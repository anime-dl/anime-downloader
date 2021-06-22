from anime_downloader.players.baseplayer import BasePlayer
from anime_downloader.players.mpv import get_mpv_configfile
from anime_downloader import config
from anime_downloader.config import Config

import os


class iina(BasePlayer):
    name = 'iina'

    STOP = 50
    NEXT = 51
    CONNECT_ERR = 2

    def _get_executable_windows(self):
        return 'iina.exe'

    def _get_executable_posix(self):
        return 'iina'

    @property
    def args(self):
        # Doesnt use the referer if it's none
        launchArgs = Config['watch']['iina_arguments']
        if self.episode.source().referer:
            return ['--keep-running',
                    '--input-conf=' + get_mpv_configfile(),
                    '--http-header-fields=referer: ' + str(self.episode.source().referer),
                    self.episode.source().stream_url, launchArgs]
        else:
            return ['--keep-running',
                    '--input-conf=' + get_mpv_configfile(),
                    self.episode.source().stream_url, launchArgs]

