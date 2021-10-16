import os, subprocess, logging
from anime_downloader.config import Config
from anime_downloader.const import get_random_header
from requests.structures import CaseInsensitiveDict

logger = logging.getLogger(__name__)


def _fmt_headers(headers):
    return '\r\n'.join([
        f'{k}: {v}'
        for k, v in headers.items()])


class PlayerOptions:
    """
    Provides input to Player implementations that they may honour.

    Parameters / Attributes
    ----------
    headers: dict
        HTTP headers.
    user_agent: str
        HTTP User-Agent header, overrides one in the headers.
    referer: str
        HTTP Referer header, overrides one in the headers.
    start: bool
        True = play, False or None = just add.
    title: str
        Pretty window title or filename.
    ep_range: str
        Episode range (Android specific).
    meta_*: str
        Cosmetic strings.
    """

    def __init__(self, **kwargs):
        __var = ('user_agent', 'referer', 'start', 'title', 'ep_range',
                 'meta_anime', 'meta_episode', 'meta_url')
        try: self.headers = CaseInsensitiveDict(kwargs['headers'])
        except KeyError: self.headers = CaseInsensitiveDict()
        for i in __var:
            try: setattr(self, i, kwargs[i])
            except KeyError:
                # user_agent
                if i is __var[0]:
                    setattr(self, i, [j for j in get_random_header().values()][0])
                else: setattr(self, i, None)

        if self.user_agent: self.headers['User-Agent'] = self.user_agent
        if self.referer: self.headers['Referer'] = self.referer

        if not self.title and self.meta_anime and self.meta_episode:
            self.title=f'{self.meta_anime} - Episode {meta_episode}'


class Player():
    """
    Functions here return arguments or the executable.
    It's recommended to override args() alongside
    _get_executable_windows() and _get_executable_posix()
    Called by:
        commands/dl.py
        commands/ezdl.py
        commands/watch.py
        gui.py
    """

    name = ''

    STOP = 0
    NEXT = PREV = CONNECT_ERR = 1

    def args(self, file='', opts=PlayerOptions()):
        return [file]

    def __init__(self, path=None):
        self.path = path if path else None

    def _get_executable_windows():
        raise LookupError

    def _get_executable_posix():
        raise LookupError

    def _get_executable(self):
        if self.path: return self.path
        else:
            try:
                ret = Config['players'][self.name]['path']
                if ret: return ret
            except KeyError: pass

        if os.name == 'nt': return self._get_executable_windows()
        else: return self._get_executable_posix()

    def play(self, file=None, opts=PlayerOptions(), episode=None):
        """
        Launches a player according to input.

        Parameters
        ----------
        file: str
            URL or path to file.
        episode: object
            When it's provided, some of the arguments are rewritten.
        opts: PlayerOptions
            Player options.

        Returns
        -------
        :py:class:`subprocess.Popen`
            An object with the process opened.
        """
        if episode:
            logger.debug(f'play: {episode._parent.title} / {episode.title} / {episode.ep_no}')
            ti, ep = f'{episode._parent.title}', f'{episode.ep_no}'
            self.opts = PlayerOptions(headers=episode.source().headers,
                                      referer=episode.source().referer,
                                      title=f'{ti} - Episode {ep}',
                                      meta_anime=ti,
                                      meta_episode=ep,
                                      meta_url=f'{episode.url}')
            file = episode.source().stream_url

        cmd = [self._get_executable()] + self.args(file, opts)
        logger.debug(f'Command: {cmd}')
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        return self.process
