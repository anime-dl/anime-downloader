from anime_downloader.players import get_player, PlayerOptions
import os


__t = 'Test - Episode 1'
__h = {'User-Agent': 'a/1.2 (b; c) d', 'Referer': 'https://example.org'}


class TestMPV:
    def setup(self):
        self.player = get_player('mpv',
            opts=PlayerOptions(title=__t,
                               headers=__h))

    def test_args(self):
        for i in self.player.args():
            if __t in i: break
        else: raise AssertionError
        for i in self.player.args():
            if __h['User-Agent'] in i and __h['Referer'] in i: break
        else: raise AssertionError

        assert len(self.player.args()) >= 4 and len(self.player.args()) <= 5

    def test_exe(self):
        exe = self.player._get_executable()
        if os.name == 'nt':
            assert 'mpv.exe' in exe
        else:
            assert 'mpv' in exe

    def test_mpv_config_file():
        assert self.player.get_mpv_configfile().endswith('mpv-config.conf')
