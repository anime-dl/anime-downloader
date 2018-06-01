from anime_downloader.sites.anime import BaseAnime
from anime_downloader.sites.nineanime import NineAnime

try:
    from anime_downloader.sites.kissanime import Kissanime
except ImportError:
    CFSCRAPE = False

import inspect

ALL_ANIME_CLASSES = [
    anime
    for name, anime in globals().items()
    if inspect.isclass(anime) and issubclass(anime, BaseAnime) and not name.startswith('Base')
]


def get_anime_class(url):
    for cls in ALL_ANIME_CLASSES:
        if cls.verify_url(url):
            return cls
