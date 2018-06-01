from anime_downloader import util, config
from anime_downloader.sites.nineanime import NineAnime

import os
import sys
import pickle
import logging
import click
from fuzzywuzzy import process


class Watcher:
    WATCH_FILE = os.path.join(config.APP_DIR, 'watch.json')

    def __init__(self):
        pass

    def new(self, url):
        anime = AnimeInfo(url)

        self._append_to_watch_file(anime)

        logging.info('Added {:.50} to watch list.'.format(anime.title))

    def list(self):
        animes = self._read_from_watch_file()

        click.echo('{:>5} | {:^35} | {:^8} | {:^10}'.format('SlNo', 'Name', 'Eps', 'Type'))
        click.echo('-'*65)
        fmt_str = '{:5} | {:35.35} |  {:3}/{:<3} | {meta:10.10}'

        for idx, anime in enumerate(animes):
            meta = anime.meta
            click.echo(fmt_str.format(idx+1, anime.title,
                                      *anime.progress(),
                                      meta=meta.get('Type', '')))

    def get(self, anime_name):
        animes = self._read_from_watch_file()

        match = process.extractOne(anime_name, animes, score_cutoff=10)

        return match[0]

    def _append_to_watch_file(self, anime):
        if not os.path.exists(self.WATCH_FILE):
            with open(self.WATCH_FILE, 'wb') as watch_file:
                pickle.dump([anime], watch_file)
            return

        with open(self.WATCH_FILE, 'rb') as watch_file:
            data = pickle.load(watch_file)

        data.append(anime)

        with open(self.WATCH_FILE, 'wb') as watch_file:
            pickle.dump(data, watch_file)

    def _read_from_watch_file(self):
        if not os.path.exists(self.WATCH_FILE):
            logging.error('Add something to watch list first.')
            sys.exit(-1)

        with open(self.WATCH_FILE, 'rb') as watch_file:
            data = pickle.load(watch_file)

        return data


class AnimeInfo(NineAnime):
    def __init__(self, *args, **kwargs):
        self.episodes_done = kwargs.pop('epiosdes_done', 0)

        super(NineAnime, self).__init__(*args, **kwargs)

    def progress(self):
        return (self.episodes_done, len(self))
