from importlib import import_module

ALL_ANIME_SITES = [
    # ('filename', 'sitename', 'classname')
    # ('_4anime', '4anime', 'Anime4'),
    ('anitube', 'anitube', 'AniTube'),
    ('animtime', 'animtime', 'AnimTime'),
    # ('anime8', 'anime8', 'Anime8'),
    ('animebinge', 'animebinge', 'AnimeBinge'),
    # ('animechameleon', 'gurminder', 'AnimeChameleon'), # Gone
    # ('animedaisuki', 'animedaisuki', 'Animedaisuki'), # Under maintenance?
    # ('animeflix', 'animeflix', 'AnimeFlix'),
    ('animeflv', 'animeflv', 'Animeflv'), # Shows as timed out, but loads in the browser
    # ('animefreak', 'animefreak', 'AnimeFreak'), # Gone, Problem loading page
    ('animefree','animefree','AnimeFree'),
    # ('animefrenzy','animefrenzy','AnimeFrenzy'),
    ('animekisa','animekisa','AnimeKisa'),
    # ('animetake','animetake','AnimeTake'), # Cloudflare
    ('animeonline','animeonline360','AnimeOnline'),
    # ('animeout', 'animeout', 'AnimeOut'), # Cloudflare
    # ('animepahe', 'animepahe', 'AnimePahe'),
    ('animerush', 'animerush', 'AnimeRush'), 
    # ('animesimple', 'animesimple', 'AnimeSimple'), # Needs some work, might still work
    ('animestar', 'animestar', 'AnimeStar'),
    # ('animesuge', 'animesuge', 'AnimeSuge'), # Gone, Problem loading page
    ('animevibe', 'animevibe', 'AnimeVibe'),
    # ('animixplay', 'animixplay', 'AniMixPlay'), # Needs much work to fix I assume, links are prob not the same
    # ('darkanime', 'darkanime', 'DarkAnime'), # It No Load
    ('dbanimes', 'dbanimes', 'DBAnimes'),
    ('erairaws', 'erai-raws', 'EraiRaws'), # Currently under maitenance
    ('egyanime', 'egyanime', 'EgyAnime'), 
    ('genoanime', 'genoanime', 'GenoAnime'),
    ('itsaturday', 'itsaturday', 'Itsaturday'),
    ('justdubs', 'justdubs', 'JustDubs'), # Blocked on my VPN
    # ('kickass', 'kickass', 'KickAss'),
    ('kissanimex', 'kissanimex', 'KissAnimeX'),
    # ('kisscartoon', 'kisscartoon', 'KissCartoon'),
    # ('nineanime', '9anime', 'NineAnime'),
    ('nyaa', 'nyaa', 'Nyaa'),
    # ('putlockers', 'putlockers', 'PutLockers'), # Cloudflare
    ('ryuanime', 'ryuanime', 'RyuAnime'), # Needs updating links and prob just a rework of scraper
    # ('shiro', 'shiro', 'Shiro'), # Requires Login
    ('subsplease', 'subsplease', 'SubsPlease'),
    ('twistmoe', 'twist.moe', 'TwistMoe'),
    ('tenshimoe', 'tenshi.moe', 'TenshiMoe'),
    ('vidstream', 'vidstream', 'VidStream'),
    # ('voiranime', 'voiranime', 'VoirAnime'),
    ('vostfree', 'vostfree', 'VostFree'),
    ('wcostream', 'wcostream', 'WcoStream'),
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
