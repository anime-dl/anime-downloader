from anime_downloader.players.player import Player, PlayerOptions, _fmt_headers
from anime_downloader.config import Config


class PotPlayer(Player):
    name = 'potplayer'

    def _get_executable_windows(self):
        from itertools import product
        import winreg as wr
        key = None
        for i, j in product((wr.KEY_WOW64_64KEY, wr.KEY_WOW64_32KEY),
                            ('PotPlayer64', 'PotPlayer')):
            try:
                key = wr.OpenKey(wr.HKEY_CURRENT_USER, 'Software\\DAUM\\'+j,
                                 access=wr.KEY_READ | i)
                ret = wr.QueryValueEx(key, 'ProgramPath')
                if type(ret) is str:
                    Config['players'][self.name]['path'] = ret
                    return ret
            except FileNotFoundError: continue
            finally: wr.CloseKey(key)
        return 'PotPlayerMini64.exe'

    def args(self, file='', opts=PlayerOptions()):
        """
        /current    :Plays the specified content(s) within an existing instance of the program.
        /autoplay   :Plays the last played item.
        /sort       :Sorts the specified contents by name before adding them into playlist.
        /seek=time  :Starts playback of the specified/last played content from the specified time point
                    -time format is: hh:mm:ss.ms (OR specify seconds only e.g. /seek=1800 to start at 30th min)
        /sub="file" :Loads the specified subtitle(s) from the specified paths or URLs.
        """
        a = ['/add']
        for i, j in (('/headers=', _fmt_headers(opts.headers)),):
            if j: a.append(i + j)

        try:
            b = Config['players'][self.name]['arguments']
            if b: return [file] + a + [b.strip().split(' ')]
        except KeyError: pass
        return [file] + a
