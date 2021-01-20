.. anime-downloader documentation master file, created by
   sphinx-quickstart on Tue Oct  9 19:36:23 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Anime-Downloader's documentation!
============================================

Anime-Downloader helps you download your favorite anime

Features
--------

- Download or stream any episode or episode range of any anime.
- Specify the quality you want to stream or download.
- Search and download.
- Save yourselves from those malicious ads.
- Download using external downloader ([aria2](https://aria2.github.io/) recommended).
- Configurable using `config.json`. See [doc](https://github.com/vn-ki/anime-downloader/wiki/Config).

Supported Sites
---------------

- 4Anime
- AnimeBinge
- Animedaisuki
- Animeflix
- Animeflv
- Animefreak
- AnimeKisa
- AnimeOnline360
- animeout
- Animerush
- Animesimple
- Animevibe
- AnimeTake
- AniTube
- Animixplay
- Anistream
- Darkanime
- Dbanimes 
- EraiRaws
- EgyAnime - usually m3u8 (good for streaming, not so much for downloading)
- FastAni
- GurminderBoparai (AnimeChameleon)
- itsaturday
- Justdubs
- Kickassanime
- Kissanimefree
- KissanimeX
- Kisscartoon - requires Selenium
- Nyaa.si
- PutLockers
- RyuAnime
- SubsPlease
- twist.moe - requires Node.js
- tenshi.moe
- Vidstream
- Voiranime
- Vostfree


NOTE: To download from sites marked `[cloudflare]`, anime-downloader has to be installed with cloudflare support(See below);

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Contents:

   usage/installation
   usage/dl
   usage/test
   usage/watch
   usage/config
   usage/sites
   usage/api
   advanced/custom_site
   api/base_classes.rst
   api/helper_functions.rst
