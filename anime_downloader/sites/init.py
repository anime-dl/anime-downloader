from importlib import import_module

ALL_ANIME_SITES = [
    # ('filename', 'sitename', 'classname')
    ('_4anime','4anime','Anime4'),
    ('anime8','anime8','Anime8'),
    ('animechameleon', 'gurminder', 'AnimeChameleon'),
    ('animedaisuki','animedaisuki','Animedaisuki'),
    ('animeflix', 'animeflix', 'AnimeFlix'),
    ('animeflv', 'animeflv', 'Animeflv'),
    ('animefreak', 'animefreak', 'AnimeFreak'),
    ('animefree','animefree','AnimeFree'),
    ('animefrenzy','animefrenzy','AnimeFrenzy'),
    ('animekisa','animekisa','AnimeKisa'),
    ('animeonline','animeonline360','AnimeOnline'),
    ('animeout', 'animeout', 'AnimeOut'),
    ('animerush','animerush','AnimeRush'),
    ('animesimple', 'animesimple', 'AnimeSimple'),
    ('animevibe','animevibe','AnimeVibe'),  
    ('animixplay','animixplay','AniMixPlay'),
    ('darkanime', 'darkanime', 'DarkAnime'),
    ('dbanimes', 'dbanimes', 'DBAnimes'),
    # ('erairaws', 'erai-raws', 'EraiRaws'),
    ('gogoanime', 'gogoanime', 'GogoAnime'),
    ('horriblesubs', 'horriblesubs', 'HorribleSubs'),
    ('itsaturday', 'itsaturday', 'Itsaturday'),
    ('justdubs','justdubs','JustDubs'),
    ('kickass', 'kickass', 'KickAss'),
    ('kissanimex', 'kissanimex', 'KissAnimeX'),
    ('kisscartoon', 'kisscartoon', 'KissCartoon'),
    ('nyaa','nyaa','Nyaa'),
    ('ryuanime', 'ryuanime', 'RyuAnime'),
    ('twistmoe', 'twist.moe', 'TwistMoe'),
    ('vidstream','vidstream','VidStream'),
    ('voiranime','voiranime','VoirAnime'),
    ('vostfree', 'vostfree', 'VostFree'),
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
