Config
------

You can configure the tool to suit your needs by using ``anime config`` or by editing the config.json.


anime config
------


This command lets you change the configuration for anime dl from within your terminal.
::
    +--------+------------+
    |      4 | watch      |
    |      3 | siteconfig |
    |      2 | ezdl       |
    |      1 | dl         |
    |--------+------------|
    |   SlNo | settings   |
    +--------+------------+
    Select Option [1]:



This lists all options in the config, and lets you change their values by entering them.
If you select 1 (one) then it will bring all the sub-keys for that selected choice.
::
    +--------+------------------------------------+
    |     16 | url                                |
    |     15 | speed_limit                        |
    |     14 | skip_download                      |
    |     13 | selescrape_driver_binary_path      |
    |     12 | selescrape_browser_executable_path |
    |     11 | selescrape_browser                 |
    |     10 | quality                            |
    |      9 | provider                           |
    |      8 | player                             |
    |      7 | force_download                     |
    |      6 | file_format                        |
    |      5 | fallback_qualities                 |
    |      4 | external_downloader                |
    |      3 | download_dir                       |
    |      2 | chunk_size                         |
    |      1 | aria2c_for_torrents                |
    |--------+------------------------------------|
    |   SlNo | dl settings                        |
    +--------+------------------------------------+
    Select Option [1]:


Selecting a setting that has no sub-keys will get you to the value input mode.
::
    +--------+------------------------------------+
    |     16 | url                                |
    |     15 | speed_limit                        |
    |     14 | skip_download                      |
    |     13 | selescrape_driver_binary_path      |
    |     12 | selescrape_browser_executable_path |
    |     11 | selescrape_browser                 |
    |     10 | quality                            |
    |      9 | provider                           |
    |      8 | player                             |
    |      7 | force_download                     |
    |      6 | file_format                        |
    |      5 | fallback_qualities                 |
    |      4 | external_downloader                |
    |      3 | download_dir                       |
    |      2 | chunk_size                         |
    |      1 | aria2c_for_torrents                |
    |--------+------------------------------------|
    |   SlNo | dl settings                        |
    +--------+------------------------------------+
    Select Option [1]:
    Current value: False
    Input new value for aria2c_for_torrents: True


config.json
------


If you want you can directly edit the config.json.
It can be found under:

-  ``~/.config/anime-downloader`` on Linux

-  ``%appdata%\anime downloader`` on Windows

- ``~/Library/Application Support/anime downloader`` on MacOS

The default config file is given below.

::

    {
        "dl": {
            "aria2c_for_torrents": false,
            "chunk_size": "10",
            "download_dir": ".",
            "external_downloader": "{aria2}",
            "fallback_qualities": [
                "720p",
                "480p",
                "360p"
            ],
            "file_format": "{anime_title}/{anime_title}_{ep_no}",
            "force_download": false,
            "player": null,
            "provider": "twist.moe",
            "quality": "1080p",
            "skip_download": false,
            "url": false
        },
        "siteconfig": {
            "animedaisuki": {
                "servers": [
                    "official"
                ]
            },
            "animeflix": {
                "fallback_servers": [
                    "FastStream"
                ],
                "server": "AUEngine",
                "version": "sub"
            },
            "animeflv": {
                "server": "natsuki",
                "version": "subbed"
            },
            "animekisa": {
                "fallback_servers": [
                    "mp4upload",
                    "vidstream"
                ],
                "server": "gcloud"
            },
            "animerush": {
                "fallback_servers": [
                    "MP4Upload",
                    "Mp4upload Video",
                    "Youruploads Video"
                ],
                "server": "Mp4uploadHD Video"
            },
            "animesimple": {
                "server": "trollvid",
                "version": "subbed"
            },
            "anistream.xyz": {
                "version": "subbed"
            },
            "dreamanime": {
                "server": "trollvid",
                "version": "subbed"
            },
            "dubbedanime": {
                "servers": [
                    "vidstream",
                    "mp4upload",
                    "trollvid"
                ],
                "version": "dubbed"
            },
            "gogoanime": {
                "server": "cdn"
            },
            "kickass": {
                "ext_fallback_servers": [
                    "Mp4Upload",
                    "Vidcdn",
                    "Vidstreaming"
                ],
                "fallback_servers": [
                    "ORIGINAL-QUALITY-V2",
                    "HTML5-HQ",
                    "HTML5",
                    "A-KICKASSANIME",
                    "BETAPLAYER",
                    "KICKASSANIME",
                    "DEVSTREAM"
                ],
                "server": "A-KICKASSANIME"
            },
            "nineanime": {
                "server": "mp4upload"
            },
            "ryuanime": {
                "server": "trollvid",
                "version": "subbed"
            },
            "vidstream": {
                "servers": [
                    "vidstream",
                    "gcloud",
                    "mp4upload",
                    "cloud9",
                    "hydrax"
                ]
            },
            "watchmovie": {
                "fallback_servers": [
                    "fembed",
                    "yourupload",
                    "mp4upload"
                ],
                "server": "gcloud"
            }
        },
        "watch": {
            "fallback_qualities": [
                "720p",
                "480p",
                "360p"
            ],
            "log_level": "INFO",
            "provider": "twist.moe",
            "quality": "1080p"
        }
    }

.. note::
    - For the key ``file_format``, you can set ``anime_title``\ (which refers to the title of the anime) and ``ep_no`` which is the number of the epiosde.
    - If you set ``player`` in ``dl``, the tool will never download, only play in the set player.
    - If you set ``force_download``, it will redownload even if the episode has already been downloaded.
Choosing preferred server 
########
``server`` contains the preferred server. 

``servers`` contains a list of servers, used in order. Set the preferred server by changing the order of the list.

``fallback_servers`` contains a list of servers to use if the primary server is not found, used in order.
 
