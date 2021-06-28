from anime_downloader.players.player import Player, PlayerOptions
from anime_downloader.config import Config


class VLC(Player):
    name = 'vlc'

    def _get_executable_windows(self):
        from os.path import exists
        for i in ('\\Program Files\\VideoLAN\\VLC\\vlc.exe',
                  '\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe'):
            if exists(i): return i
        return 'vlc.exe'

    def _get_executable_posix(self):
        return 'vlc'

    def args(self, file='', opts=PlayerOptions()):
        """
        Note: VLC ignores --http-user-agent.

        --meta-genre=<string>       Genre metadata
        --meta-copyright=<string>   Copyright metadata
        --meta-description=<string>	Description metadata
        --meta-date=<string>        Date metadata
        """
        if opts.meta_anime:
            if opts.meta_episode:
                opts.title = opts.meta_episode
            else:
                opts.meta_anime = None
        a = ['--one-instance']
        for i, j in (('--http-user-agent=', opts.user_agent),
                     ('--http-referrer=', opts.referer),
                     ('--playlist-autostart', opts.start),
                     ('--meta-artist=', opts.meta_anime),
                     ('--meta-title=', opts.title),
                     ('--meta-url=', opts.meta_url)):
            if j:
                if type(j) is bool: a.append(i)
                else: a.append(i + j)

        try:
            b = Config['players'][self.name]['arguments']
            if b: return a + [b.strip().split(' ')] + [file]
        except KeyError: pass
        return a + [file]
