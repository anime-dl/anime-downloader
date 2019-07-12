Config
------

You can configure the tool to suit your needs by using ``config.json``.

This can be found under:

-  ``~/.config/anime-downloader`` on Linux

-  ``C:\Users\[Username]\AppData\Roaming\anime downloader`` on Windows

You can override the settings in the ``config.json``, with command line
arguments.

The default config file is given below.

.. code:: json

   {
       "dl": {
           "download_dir": ".",
           "force_download": false,
           "file_format": "{anime_title}/{anime_title}_{ep_no}",
           "log_level": "INFO",
           "player": null,
           "quality": "720p",
           "skip_download": false,
           "url": false
       },
       "watch": {
           "log_level": "INFO",
           "quality": "720p"
       }
   }

.. note::
    - For the key ``file_format``, you can set ``anime_title``\ (which refers to the title of the anime) and ``ep_no`` which is the number of the epiosde.
    - If you set ``player`` in ``dl``, the tool will never download, only play in the set player.
    - If you set ``force_download``, it will redownload even if the epiosde has already been downloaded.
