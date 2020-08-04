from anime_downloader import config
from anime_downloader.sites import get_anime_class

import os
import sys
import json
import logging
import click
import warnings
from time import time

logger = logging.getLogger(__name__)

# Don't warn if not using fuzzywuzzy[speedup]
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from fuzzywuzzy import process


class Watcher:
    WATCH_FILE = os.path.join(config.APP_DIR, 'watch.json')

    def __init__(self):
        self.sorted = None
        pass

    def new(self, url):
        AnimeInfo = self._get_anime_info_class(url)
        anime = AnimeInfo(url, timestamp=time())
        self._append_to_watch_file(anime)

        logger.info('Added {:.50} to watch list.'.format(anime.title))
        return anime

    def list(self, filt = None):
        animes = self._read_from_watch_file()
        if filt in [None, 'all']:
            animes = self._sorting_for_list(animes)
            self.sorted = True
        click.echo('{:>5} | {:^35} | {:^8} | {} | {:^10}'.format(
            'SlNo', 'Name', 'Eps','Score', 'Status'
        ))
        click.echo('-'*65)
        fmt_str = '{:5} | {:35.35} |  {:3}/{:<3} | {:^5} | {}'
        if not filt in [ None, 'all' ]:
            animes = [ i for i in animes if i.watch_status == filt ]

        for idx, anime in enumerate(animes):
            meta = anime.meta
            click.echo(click.style(fmt_str.format(idx+1,
                                        anime.title,
                                        *anime.progress(),
                                     anime.score,
                                     anime.watch_status),fg=anime.colours))

    def anime_list(self):
        return self._read_from_watch_file()

    def get(self, anime_name):
        animes = self._read_from_watch_file()
        if self.sorted == True:
            animes = self._sorting_for_list(animes)

        if isinstance(anime_name, int):
            return animes[anime_name]

        match = process.extractOne(anime_name, animes, score_cutoff=40)
        if match:
            anime = match[0]
            logger.debug('Anime: {!r}, episodes_done: {}'.format(
                anime, anime.episodes_done))

            if (time() - anime._timestamp) > 4*24*60*60:
                anime = self.update_anime(anime)
            return anime

    def update_anime(self, anime):
        if not hasattr(anime,'colours'):
            colours = {
                'watching':'blue',
                'completed':'green',
                'dropped':'red',
                'planned':'yellow',
            }
            anime.colours = colours.get(anime.watch_status,'yellow')

        if not hasattr(anime, 'meta') or not anime.meta.get('Status') or \
                anime.meta['Status'].lower() == 'airing':
            logger.info('Updating anime {}'.format(anime.title))
            AnimeInfo = self._get_anime_info_class(anime.url)
            newanime = AnimeInfo(anime.url, episodes_done=anime.episodes_done,
                                 timestamp=time())
            newanime.title = anime.title

            self.update(newanime)
            return newanime
        return anime

    def add(self, anime):
        self._append_to_watch_file(anime)

    def remove(self, anime):
        anime_name = anime.title
        animes = self._read_from_watch_file()
        animes = [anime for anime in animes if anime.title != anime_name]
        self._write_to_watch_file(animes)

    def update(self, changed_anime):
        animes = self._read_from_watch_file()
        animes = [anime for anime in animes
                  if anime.title != changed_anime.title]
        animes = [changed_anime] + animes
        self._write_to_watch_file(animes)

    def _append_to_watch_file(self, anime):
        if not os.path.exists(self.WATCH_FILE):
            self._write_to_watch_file([anime])
            return

        data = self._read_from_watch_file()
        data = [anime] + data

        self._write_to_watch_file(data)

    def _write_to_watch_file(self, animes):
        animes = [anime.__dict__ for anime in animes]
        with open(self.WATCH_FILE, 'w') as watch_file:
            json.dump(animes, watch_file)

    def _read_from_watch_file(self):
        if not os.path.exists(self.WATCH_FILE):
            logger.error('Add something to watch list first.')
            sys.exit(1)

        with open(self.WATCH_FILE, 'r') as watch_file:
            data = json.load(watch_file)

        ret = []
        for anime_dict in data:
            # For backwards compatibility
            if '_episodeIds' in anime_dict:
                anime_dict['_episode_urls'] = anime_dict['_episodeIds']

            AnimeInfo = self._get_anime_info_class(anime_dict['url'])
            anime = AnimeInfo(_skip_online_data=True)
            anime.__dict__ = anime_dict
            ret.append(anime)

        return ret

    def _sorting_for_list(self,animes):
        status_index = ['watching','completed','dropped','planned','all']
        animes = sorted(animes, key=lambda x: status_index.index(x.watch_status))
        return animes

    def _get_anime_info_class(self, url):
        cls = get_anime_class(url)

        # TODO: Maybe this is better off as a mixin
        class AnimeInfo(cls, sitename=cls.sitename):
            def __init__(self, *args, **kwargs):
                self.episodes_done = kwargs.pop('episodes_done', 0)
                self._timestamp = kwargs.pop('timestamp', 0)
                self.score = 0
                self.watch_status = 'watching'
                self.colours = 'blue'
                super(cls, self).__init__(*args, **kwargs)
            def progress(self):
                return (self.episodes_done, len(self))

        return AnimeInfo
