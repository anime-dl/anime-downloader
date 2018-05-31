import click
import os
import errno
import yaml

DEFAULT_CONFIG = {
    'dl': {
        'anime_url': None,
        'episode_range': None,
        'playlist': False,
        'url': False,
        'player': None,
        'no_download': False,
        'download_dir': '.',
        'quality': '720p',
        'force': False,
        'log_level': 'INFO'
    }
}

APP_NAME = 'anime downloader'
APP_DIR = click.get_app_dir(APP_NAME)
CONFIG_FILE = os.path.join(APP_DIR, 'config.yml')


def write_config(config_dict):
    with open(CONFIG_FILE, 'w') as configfile:
        yaml.dump(config_dict, configfile, default_flow_style=False)


def write_default_config():
    try:
        os.makedirs(APP_DIR)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    if not os.path.exists(CONFIG_FILE):
        write_config(DEFAULT_CONFIG)
