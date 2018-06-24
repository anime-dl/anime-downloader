from importlib import import_module

ALL_ANIME_SITES = [
    # ('filename', 'sitename', 'classname')
    ('nineanime', '9anime', 'NineAnime'),
    ('gogoanime', 'gogoanime', 'GogoAnime'),
    ('kissanime', 'kissanime', 'KissAnime'),
    ('kisscartoon', 'kisscartoon', 'KissCartoon'),
]


def get_anime_class(url):
    for site in ALL_ANIME_SITES:
        if site[1] in url:
            module = import_module('anime_downloader.sites.{}'.format(site[0]))
            return getattr(module, site[2])
