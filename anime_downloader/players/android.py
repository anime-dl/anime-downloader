from anime_downloader.players.player import Player, PlayerOptions
from anime_downloader.config import Config


class Android(Player):
    name = 'android'

    def _get_executable(self):
        return 'am'

    def args(self, file='', opts=PlayerOptions()):
        return ['start', '-a', 'android.intent.action.VIEW', '-t',
                'video/*', '-d', file]

    def play(self, file=None, episode=None, opts=PlayerOptions()):
        ret = super().play(file, episode, opts)
        if opts.ep_range == None or ':' in opts.ep_range and opts.ep_range != "0:1":
            input("Press enter to continue\n")
        return ret
