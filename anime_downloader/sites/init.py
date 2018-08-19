from importlib import import_module
import logging

ALL_ANIME_SITES = [
    # ('filename', 'sitename', 'classname')
    ('nineanime', '9anime', 'NineAnime'),
    ('gogoanime', 'gogoanime', 'GogoAnime'),
    ('kissanime', 'kissanime', 'KissAnime'),
    ('kisscartoon', 'kisscartoon', 'KissCartoon'),
    ('masterani', 'masterani', 'Masterani'),
    ('twistmoe', 'twist.moe', 'TwistMoe'),
    ('animepahe', 'animepahe', 'AnimePahe')
]


def get_anime_class(url):
    for site in ALL_ANIME_SITES:
        if site[1] in url:
            try:
                module = import_module(
                    'anime_downloader.sites.{}'.format(site[0])
                )
            except ImportError as e:
                # TODO: This should raise an error instead of logging.
                # I'm lazy af right now.
                raise
                logging.debug("Coudn't import {}, '{}'".format(site[0], e.msg))
                logging.warning("Provider '{}' not used. Make sure you have "
                                "cfscrape and node-js installed".format(
                                    site[0])
                                )
                continue

            return getattr(module, site[2])
