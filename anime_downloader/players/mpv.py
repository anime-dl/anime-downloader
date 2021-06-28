from anime_downloader.players.player import Player, PlayerOptions, _fmt_headers
from anime_downloader import config
from anime_downloader.config import Config

import os


class MPV(Player):
    name = 'mpv'

    STOP = 50
    NEXT = 51
    PREV = 52
    CONNECT_ERR = 2

    def _get_executable_windows(self):
        return 'mpv.exe'

    def _get_executable_posix(self):
        return 'mpv'

    def args(self, file='', opts=PlayerOptions()):
        a = list()
        for i, j in (('--http-header-fields=', _fmt_headers(opts.headers)),
                     ('--title=', opts.title),
                     ('--input-conf=', get_mpv_configfile())):
            if j: a.append(i + j)

        try:
            b = Config['players'][self.name]['arguments']
            if b: return a + [b.strip().split(' ')] + [file]
        except KeyError: pass
        return a + [file]


def get_mpv_home():
    if 'MPV_HOME' in os.environ:
        return os.environ.get('MPV_HOME')
    elif 'XDG_CONFIG_HOME' in os.environ:
        return os.path.join(os.environ.get('XDG_CONFIG_HOME'), 'mpv')
    elif os.path.exists(os.path.expanduser('~/.mpv')):
        return os.path.expanduser('~/.mpv')
    elif os.name == 'posix':
        return os.path.expanduser('~/.config/mpv')
    else:
        return os.path.join(os.environ.get('APPDATA'), 'mpv')


def get_mpv_configfile():
    # Read the user's input config file if it exists
    userconf = os.path.join(get_mpv_home(), 'input.conf')
    userconftext = ''
    if os.path.exists(userconf):
        with open(userconf, 'r') as userconfigfile:
            userconftext = userconfigfile.read()

    # Create a new config file to add anime-downloader specific key bindings
    conf = os.path.join(config.APP_DIR, 'mpv-config.conf')
    with open(conf, 'w') as configfile:
        configfile.write(
            userconftext +
            'q quit 50\nCLOSE_WIN quit 50\nSTOP quit 50\nctrl+c quit 50\n'
            '> quit 51\nNEXT quit 51\n< quit 52\nPREV quit 52\ni seek 80\n'
        )

    return conf
