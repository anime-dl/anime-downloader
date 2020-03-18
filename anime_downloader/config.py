import click
import os
import errno
import json
from anime_downloader import util

APP_NAME = 'anime downloader'
APP_DIR = click.get_app_dir(APP_NAME)
DEFAULT_CONFIG = {
    'dl': {
        'url': False,
        'player': None,
        'skip_download': False,
        'download_dir': '.',
        'quality': '1080p',
        'fallback_qualities': ['720p', '480p', '360p'],
        'force_download': False,
        'file_format': '{anime_title}/{anime_title}_{ep_no}',
        'provider': 'twist.moe',
        'external_downloader': '',
    },
    'watch': {
        'quality': '1080p',
        'fallback_qualities': ['720p', '480p', '360p'],
        'log_level': 'INFO',
        'provider': 'twist.moe',
    },
    "siteconfig": {
        "nineanime": {
            "server": "mp4upload",
        },
        'anistream.xyz': {
            "version": "subbed",
        },
        'animeflv': {
            "version": "subbed",
            "server": "natsuki",
        },
        'gogoanime': {
            "server": "cdn",
        }
    }
}


class _Config:
    CONFIG_FILE = os.path.join(APP_DIR, 'config.json')

    def __init__(self):
        try:
            os.makedirs(APP_DIR)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        if not os.path.exists(self.CONFIG_FILE):
            self._write_default_config()
            self._CONFIG = DEFAULT_CONFIG
        else:
            self._CONFIG = self._read_config()

            def update(gkey, to_be, from_dict):
                if gkey not in to_be:
                    to_be[gkey] = {}
                for key, val in from_dict[gkey].items():
                    if key not in to_be[gkey].keys():
                        to_be[gkey][key] = val
                    elif isinstance(from_dict[gkey][key], dict):
                        update(key, to_be[gkey], from_dict[gkey])

            for key in DEFAULT_CONFIG.keys():
                update(key, self._CONFIG, DEFAULT_CONFIG)
            self.write()
            # Expand environment variables in download_dir (#222)
            download_dir = self._CONFIG['dl']['download_dir']
            download_dir = os.path.expandvars(download_dir)
            self._CONFIG['dl']['download_dir'] = download_dir

    @property
    def CONTEXT_SETTINGS(self):
        return dict(
            default_map=self._CONFIG
        )

    def __getitem__(self, attr):
        return self._CONFIG[attr]

    def write(self):
        self._write_config(self._CONFIG)

    def _write_config(self, config_dict):
        with open(self.CONFIG_FILE, 'w') as configfile:
            json.dump(config_dict, configfile, indent=4, sort_keys=True)

    def _read_config(self):
        with open(self.CONFIG_FILE, 'r') as configfile:
            conf = json.load(configfile)
        return conf

    def _write_default_config(self):
        if util.check_in_path('aria2c'):
            DEFAULT_CONFIG['dl']['external_downloader'] = '{aria2}'
        self._write_config(DEFAULT_CONFIG)


Config = _Config()
