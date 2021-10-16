from importlib import import_module

ALL_PLAYERS = [
    # ('filename', 'classname')
    ('android', 'Android'),
    ('mpv', 'MPV'),
    ('potplayer', 'PotPlayer'),
    ('vlc', 'VLC')
]

__instance = None


def get_player(s):
    global __instance
    """
    Instatiates a class corresposing to string setting s and returns it.
    See :py:data:`anime_downloader.players.ALL_PLAYERS` for all classes.

    Parameters
    ----------
    s: str
        String setting corresponding to the module. It can be a module
        name or the executable path.

    Returns
    -------
    :py:class:`anime_downloader.players.Player`
        Instance of :py:class:`anime_downloader.players.Player`
    """
    try:
        for i, j in ALL_PLAYERS:
            if i == s.lower():
                if type(__instance).__name__ != j:
                    __instance = getattr(import_module(f'anime_downloader.players.{i}'), j)()
                break
        else: raise ImportError
    except ImportError:
        if __instance and __instance.path != s:
            __instance = getattr(import_module('anime_downloader.players.player'), 'Player')(path=s)
    return __instance
