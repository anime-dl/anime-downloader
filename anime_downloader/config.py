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
        'chunk_size': '10',
        'fallback_qualities': ['720p', '480p', '360p'],
        'force_download': False,
        'file_format': '{anime_title}/{anime_title}_{ep_no}',
        'provider': 'twist.moe',
        'external_downloader': '',
        'aria2c_for_torrents': False,
        'selescrape_browser': None,
        'selescrape_browser_executable_path' : None,
        'selescrape_driver_binary_path' : None,
        'speed_limit' : 0,
    },
    'watch': {
        'quality': '1080p',
        'fallback_qualities': ['720p', '480p', '360p'],
        'log_level': 'INFO',
        'provider': 'twist.moe',
        'autoplay_next':True
    },
    "siteconfig": {
        'animefrenzy': {
            "version": "subbed"
        },
        'animixplay': {
            "server": "vidstream",
        },
        'nineanime': {
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
        },
        'animerush':{
            "servers": ["Mp4uploadHD Video","MP4Upload", "Mp4upload Video", "Youruploads Video"]
        },
        'kickass': {
            "server": "A-KICKASSANIME",
            "fallback_servers": ["ORIGINAL-QUALITY-V2","HTML5-HQ","HTML5","A-KICKASSANIME","BETAPLAYER","KICKASSANIME","DEVSTREAM"],
            "ext_fallback_servers": ["Mp4Upload","Vidcdn","Vidstreaming"],
        },
        'animesimple': {
            "version": "subbed",
            "servers": ["vidstreaming","trollvid","mp4upload","xstreamcdn"]
        },
        'darkanime': {
            "version": "subbed",
            "servers": ["mp4upload","trollvid"],
        },
        'dreamanime': {
            "version": "subbed",
            "server": "trollvid",
        },
        'ryuanime': {
            "version": "subbed",
            "server": "trollvid",
        },
        'animekisa': {
            "server": "gcloud",
            "fallback_servers": ["mp4upload","vidstream"]
        },
        
        'watchmovie': {
            "servers": ["vidstream",'gcloud','yourupload','hydrax']
        },
        'animeflix': {
            "server": "AUEngine",
            "fallback_servers": ["FastStream"],
            "version": "sub",
        },
        'dubbedanime': {
            "servers": ["vidstream","mp4upload","trollvid"],
            "version": "dubbed",
        },
        'animedaisuki': {
            "servers": ["official"]
        },
        'nyaa': {
            "filter": "Trusted only",
            "category": "English-translated"
        },
        'vidstream': {
            "servers": ["vidstream","vidstream_bk","gcloud","mp4upload","cloud9","hydrax","mixdrop"]
        },
        'justdubs': {
            "servers": ["mp4upload","gcloud"]
        },
        'kisscartoon': {
            "servers": [
                "mpserver",
                "yuserver",
                "oserver",
                "xserver",
                "ptserver"
            ]
        },
        'animevibe': {
            "servers": [
                "vidstream",
                "3rdparty",
                "mp4upload",
                "hydrax",
                "gcloud",
                "fembed"
            ]
        },
        'yify': {
            "servers": [
                "vidstream",
                "yify"
            ]
        },
        'vostfree': {
            'server': 'sibnet'
        },
        'voiranime': {
            "servers":[
                "gounlimited"
            ]
        },
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
            try:
                conf = json.load(configfile)
            except:
                raise SyntaxWarning('The config file is not correctly formatted')
        return conf

    def _write_default_config(self):
        if util.check_in_path('aria2c'):
            DEFAULT_CONFIG['dl']['external_downloader'] = '{aria2}'
        self._write_config(DEFAULT_CONFIG)


Config = _Config()
