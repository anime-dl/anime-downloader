from anime_downloader.players.baseplayer import BasePlayer
from anime_downloader import config

import os


class mpv(BasePlayer):
    name = 'mpv'

    STOP = 50
    NEXT = 51
    CONNECT_ERR = 2

    def _get_executable_windows(self):
        return 'mpv.exe'

    def _get_executable_posix(self):
        return 'mpv'

    @property
    def args(self):
        return ['--input-conf='+get_mpv_configfile(), self.stream_url]


def get_mpv_configfile():
    conf = os.path.join(config.APP_DIR, 'mpv-config.conf')

    # TODO: Use available config too(?)

    # For now don't do this
    # if os.path.exists(conf):
    #     return conf

    with open(conf, 'w') as configfile:
        configfile.write(
            'q quit 50\nCLOSE_WIN quit 50\nSTOP quit 50\nctrl+c quit 50\n'
            '> quit 51\nNEXT quit 51\n< quit 52\nPREV quit 52\ni seek 80\n'
        )

    return conf
