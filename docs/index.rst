.. anime-downloader documentation master file, created by
   sphinx-quickstart on Tue Oct  9 19:36:23 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to anime-downloader's documentation!
============================================

anime-downloader helps you download your favorite anime

Features
--------

- Download or stream any episode or episode range of any anime.
- Specify the quality you want to stream or download.
- Search and download.
- Save yourselves from those malicious ads.
- Add any anime to your watch list using `anime watch` and let anime downloader take care of everything for you.
- Download using external downloader ([aria2](https://aria2.github.io/) recommended).
- Configurable using `config.json`. See [doc](https://github.com/vn-ki/anime-downloader/wiki/Config).

Supported Sites
---------------

- 9anime
- twist.moe
- KissAnime [cloudflare]
- Masterani.me [cloudlfare]
- KissCartoon [cloudflare]
- Gogoanime
- AnimePahe [cloudflare]

NOTE: To download from sites marked `[cloudflare]`, anime-downloader has to be installed with cloudflare support(See below).

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Contents:

   usage/installation
   usage/dl
   usage/watch
   usage/config
   advanced/custom_site
   api/anime.rst
