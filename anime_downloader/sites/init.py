from importlib import import_module

ALL_ANIME_SITES = [
    # ('filename', 'sitename', 'classname')
    ('gogoanime', 'gogoanime', 'GogoAnime'),
    ('kissanime', 'kissanime', 'KissAnime'),
    ('kisscartoon', 'kisscartoon', 'KissCartoon'),
    ('twistmoe', 'twist.moe', 'TwistMoe'),
    ('animepahe', 'animepahe', 'AnimePahe'),
    ('animeflv', 'animeflv', 'Animeflv'),
    ('itsaturday', 'itsaturday', 'Itsaturday'),
    ('animefreak', 'animefreak', 'AnimeFreak'),
    ('animeflix', 'animeflix', 'AnimeFlix'),
    ('dubbedanime', 'dubbedanime', 'Dubbedanime'),
    ('animeout', 'animeout', 'AnimeOut'),
    ('animerush','animerush','AnimeRush'),
    ('animesimple', 'animesimple', 'AnimeSimple'),
    ('kickass', 'kickass', 'KickAss'),
    ('dreamanime', 'dreamanime', 'DreamAnime'),
    ('ryuanime', 'ryuanime', 'RyuAnime'),
    ('erairaws', 'erai-raws', 'EraiRaws'),
    ('watchmovie','watchmovie','WatchMovie'),
    ('animekisa','animekisa','AnimeKisa'),
    ('nyaa','nyaa','Nyaa'),
    ('animedaisuki','animedaisuki','Animedaisuki')
]


def get_anime_class(url):
    """
    Get anime class corresposing to url or name.
    See :py:data:`anime_downloader.sites.ALL_ANIME_SITES` to get the possible anime sites.

    Parameters
    ----------
    url: string
        URL of the anime.

    Returns
    -------
    :py:class:`anime_downloader.sites.anime.Anime`
        Concrete implementation of :py:class:`anime_downloader.sites.anime.Anime`
    """
    for site in ALL_ANIME_SITES:
        if site[1] in url:
            try:
                module = import_module(
                    'anime_downloader.sites.{}'.format(site[0])
                )
            except ImportError:
                raise
            return getattr(module, site[2])
