from anime_downloader import config
from anime_downloader.sites import get_anime_class, ALL_ANIME_SITES

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

    def list(self, filt=None):
        animes = self._read_from_watch_file()
        if filt in [None, 'all']:
            animes = self._sorting_for_list(animes)
            self.sorted = True
        click.echo('{:>5} | {:^35} | {:^8} | {} | {:^10}'.format(
            'SlNo', 'Name', 'Eps', 'Score', 'Status'
        ))
        click.echo('-' * 65)
        fmt_str = '{:5} | {:35.35} |  {:3}/{:<3} | {:^5} | {}'
        if not filt in [None, 'all']:
            animes = [i for i in animes if i.watch_status == filt]

        for idx, anime in enumerate(animes):
            meta = anime.meta
            click.echo(click.style(fmt_str.format(idx + 1,
                                                  anime.title,
                                                  *anime.progress(),
                                                  anime.score,
                                                  anime.watch_status), fg=anime.colours))

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

            if (time() - anime._timestamp) > 4 * 24 * 60 * 60:
                anime = self.update_anime(anime)
            return anime

    def update_anime(self, anime):
        if not hasattr(anime, 'colours'):
            colours = {
                'watching': 'cyan',
                'completed': 'green',
                'dropped': 'red',
                'planned': 'yellow',
                'hold': 'white'
            }
            anime.colours = colours.get(anime.watch_status, 'yellow')

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

    def _write_to_watch_file(self, animes, MAL_import=False):
        if not MAL_import:
            animes = [anime.__dict__ for anime in animes]

        with open(self.WATCH_FILE, 'w') as watch_file:
            json.dump(animes, watch_file)

    def _import_from_MAL(self, PATH):
        import xml.etree.ElementTree as ET  # Standard Library import, conditional as it only needs to be imported for this line
        root = ET.parse(PATH).getroot()
        list_to_dict = []
        values = {'Plan to Watch': {'planned': 'yellow'},
                  'Completed': {'completed': 'green'},
                  'Watching': {'watching': 'cyan'},
                  'Dropped': {'dropped': 'red'},
                  'On-Hold': {'hold': 'white'}
                  }
        for type_tag in root.findall('anime'):
            mal_watched_episodes = type_tag.find('my_watched_episodes').text
            mal_score = type_tag.find('my_score').text
            mal_watch_status = type_tag.find('my_status').text
            colour = str(list(values[mal_watch_status].values())[0])
            mal_watch_status = str(list(values[mal_watch_status].keys())[0])
            mal_title = type_tag.find('series_title').text
            mal_episodes = type_tag.find('series_episodes').text
            mal_ID = type_tag.find('series_animedb_id').text
            #We have to initialise some values for when we add anime from MAL. Now, we do this instead of letting the user choose the provider 
            #On first run, this is so the user doesn't have to manually do hundreds of entries. The values initialise to one of the sites we already have 
            #But with a broken link, the provider needs to be set manually for a series by using the set command in the list.
            list_to_dict.append({
                "episodes_done": int(mal_watched_episodes),
                "_timestamp": time(),
                "score": int(mal_score),
                "watch_status": mal_watch_status,
                "colours": colour,
                'mal_ID': int(mal_ID),
                "url": ALL_ANIME_SITES[0][1],
                "_fallback_qualities": ["720p", "480p", "360p"],
                "quality": "720p",
                "title": mal_title,
                "_episode_urls": [[1, "https://notarealwebsite.illusion/"]],
                "_len": int(mal_episodes)
            })
            self._write_to_watch_file(list_to_dict, MAL_import=True)
        logger.warn("MAL List has been imported, please initialise the sites by using the 'set' command on a list entry!")

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

    def _sorting_for_list(self, animes):
        status_index = ['watching', 'completed', 'dropped', 'planned', 'hold', 'all']
        animes = sorted(animes, key=lambda x: status_index.index(x.watch_status))
        return animes

    def _get_anime_info_class(self, url):
        cls = get_anime_class(url)
        if not cls:
            logger.warn(f"The url: {url} is no longer supported. The provider needs to be set manually upon selection.") 
            
            """
            Provides some level of backcompatability when watch lists have providers that have been removed. They are then warned via logger that they will 
            have to change providers using the set function when an anime is selected in the list. 
            """
            url = ALL_ANIME_SITES[0][1] 
            cls = get_anime_class(url)

        # TODO: Maybe this is better off as a mixin
        class AnimeInfo(cls, sitename=cls.sitename):
            def __init__(self, *args, **kwargs):
                self.episodes_done = kwargs.pop('episodes_done', 0)
                self._timestamp = kwargs.pop('timestamp', 0)
                # Initial values needed for MAL which can't be got yet from just a simple addition to the watch list.
                self.score = 0
                self.watch_status = 'watching'
                self.colours = 'blue'
                self.mal_ID = 0
                super(cls, self).__init__(*args, **kwargs)

            def progress(self):
                return (self.episodes_done, len(self))

        return AnimeInfo
