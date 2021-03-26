from importlib import import_module

ALL_ANIME_SITES = [
    # ('filename', 'sitename', 'classname')
    ('_4anime', '4anime', 'Anime4'),
    ('anitube', 'anitube', 'AniTube'),
    ('anime8', 'anime8', 'Anime8'),
    ('animebinge', 'animebinge', 'AnimeBinge'),
    ('animechameleon', 'gurminder', 'AnimeChameleon'),
    ('animedaisuki', 'animedaisuki', 'Animedaisuki'),
    ('animeflix', 'animeflix', 'AnimeFlix'),
    ('animeflv', 'animeflv', 'Animeflv'),
    ('animefreak', 'animefreak', 'AnimeFreak'),
    ('animefree','animefree','AnimeFree'),
    ('animefrenzy','animefrenzy','AnimeFrenzy'),
    ('animekisa','animekisa','AnimeKisa'),
    ('animetake','animetake','AnimeTake'),
    ('animeonline','animeonline360','AnimeOnline'),
    ('animeout', 'animeout', 'AnimeOut'),
    ('animerush', 'animerush', 'AnimeRush'),
    ('animesimple', 'animesimple', 'AnimeSimple'),
    ('animesuge', 'animesuge', 'AnimeSuge'),
    ('animevibe', 'animevibe', 'AnimeVibe'),
    ('animixplay', 'animixplay', 'AniMixPlay'),
    ('darkanime', 'darkanime', 'DarkAnime'),
    ('dbanimes', 'dbanimes', 'DBAnimes'),
    ('erairaws', 'erai-raws', 'EraiRaws'),
    ('egyanime', 'egyanime', 'EgyAnime'),
    ('genoanime', 'genoanime', 'GenoAnime'),
    ('itsaturday', 'itsaturday', 'Itsaturday'),
    ('justdubs', 'justdubs', 'JustDubs'),
    # ('kickass', 'kickass', 'KickAss'),
    ('kissanimex', 'kissanimex', 'KissAnimeX'),
    # ('kisscartoon', 'kisscartoon', 'KissCartoon'),
    # ('nineanime', '9anime', 'NineAnime'),
    ('nyaa', 'nyaa', 'Nyaa'),
    ('putlockers', 'putlockers', 'PutLockers'),
    ('ryuanime', 'ryuanime', 'RyuAnime'),
    ('shiro', 'shiro', 'Shiro'),
    ('subsplease', 'subsplease', 'SubsPlease'),
    ('twistmoe', 'twist.moe', 'TwistMoe'),
    ('tenshimoe', 'tenshi.moe', 'TenshiMoe'),
    ('vidstream', 'vidstream', 'VidStream'),
    # ('voiranime', 'voiranime', 'VoirAnime'),
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
