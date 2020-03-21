from anime_downloader.players.mpv import mpv, get_mpv_configfile
import os


# class TestMPV:
#     def setup(self):
#         self.player = mpv('example.mp4')

#     def test_args(self):
#         assert len(self.player.args) == 2

#     def test_exe(self):
#         exe = self.player._get_executable()
#         if os.name == 'nt':
#             assert 'mpv.exe' in exe
#         else:
#             assert 'mpv' in exe


def test_mpv_config_file():
    assert get_mpv_configfile().endswith('mpv-config.conf')
