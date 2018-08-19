import click
import os
import errno
import json

APP_NAME = 'anime downloader'
APP_DIR = click.get_app_dir(APP_NAME)
DEFAULT_CONFIG = {
    'dl': {
        'url': False,
        'player': None,
        'skip_download': False,
        'download_dir': '.',
        'quality': '720p',
        'fallback_qualities': ['720p', '480p', '360p'],
        'force_download': False,
        'log_level': 'INFO',
        'file_format': '{anime_title}/{anime_title}_{ep_no}',
        'provider': '9anime',
        'external_downloader': '',
    },
    'watch': {
        'quality': '720p',
        'log_level': 'INFO',
        'provider': '9anime',
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

            def update(gkey):
                for key, val in DEFAULT_CONFIG[gkey].items():
                    if key not in self._CONFIG[gkey].keys():
                        self._CONFIG[gkey][key] = val

            for key in ['dl', 'watch']:
                update(key)
            self.write()

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
        self._write_config(DEFAULT_CONFIG)


Config = _Config()
