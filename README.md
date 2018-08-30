# Anime Downloader

[![Build Status](https://travis-ci.com/vn-ki/anime-downloader.svg?branch=master)](https://travis-ci.com/vn-ki/anime-downloader)
[![codecov](https://codecov.io/gh/vn-ki/anime-downloader/branch/master/graph/badge.svg)](https://codecov.io/gh/vn-ki/anime-downloader)
[![PyPI pyversions](https://img.shields.io/badge/python-3.3%2B-blue.svg)](https://pypi.org/project/anime-downloader/)
[![PyPI](https://img.shields.io/pypi/v/anime-downloader.svg)](https://pypi.org/project/anime-downloader/)
[![Discord](https://img.shields.io/discord/483008720167632929.svg)](https://discord.gg/Qn2nWGm)

<!-- #### NOTE: **9anime support has been experiencing issues for the past week. It might work but not 100% reliable. Kissanime still works as expected.** -->

Ever dreamt about watching anime for free effortlessly without all those unbearable ads? Ever dreamt of downloading your favourite anime for that long trip?

![kawaii](https://thumbs.gfycat.com/IgnorantYoungDowitcher-size_restricted.gif)

Yeah. Me too! That's why this tool exists.

## Features

- Download or stream any episode or episode range of any anime.
- Specify the quality you want to stream or download.
- Search and download.
- Save yourselves from those malicious ads.
- Add any anime to your watch list using `anime watch` and let anime downloader take care of everything for you.
- Download using external downloader ([aria2](https://aria2.github.io/) recommended).
- Configurable using `config.json`. See [doc](https://github.com/vn-ki/anime-downloader/wiki/Config).

## Supported Sites

<!-- [![CircleCI](https://circleci.com/gh/vn-ki/anime-downloader/tree/master.svg?style=svg)](https://circleci.com/gh/vn-ki/anime-downloader/tree/master) -->

- 9anime
- twist.moe
- KissAnime [cloudflare]
- Masterani.me [cloudlfare]
- KissCartoon [cloudflare]
- Gogoanime
- AnimePahe [cloudflare]

NOTE: To download from sites marked `[cloudflare]`, anime-downloader has to be installed with cloudflare support(See below).

## Installation

You can install the stable release from PyPI.
```bash
$ pip install anime-downloader
```

To install with cloudflare support, (Read note below)
```bash
$ pip install anime-downloader[cloudflare]
```

To install the dev version
```bash
$ pip install -U git+https://github.com/vn-ki/anime-downloader.git

# To install with cloudflare support
$ pip install -U git+https://github.com/vn-ki/anime-downloader.git#egg=anime-downloader[cloudflare]
```

If you have trouble installing, see extended installation instructions [here](https://github.com/vn-ki/anime-downloader/wiki/Installation).

**NOTE**:
- For cloudflare scraping [cfscrape](https://github.com/Anorov/cloudflare-scrape) is used. It depends on [`node-js`](https://nodejs.org/en/). So if you want to use cloudflare, make sure you have [node-js](https://nodejs.org/en/) installed.
- You might have to use pip3 depending on your system
- If you are using zsh, don't forget to escape `[` and `]` using `\`.

## Usage

See [wiki](https://github.com/vn-ki/anime-downloader/wiki).

Anime downloader has two sub commands, `dl` and `watch`.

- [dl](https://github.com/vn-ki/anime-downloader/wiki/dl-command): `dl` can download anime.
- [watch](https://github.com/vn-ki/anime-downloader/wiki/watch-command): `watch` can manage your anime watch list. Needs [mpv](https://mpv.io). With `watch` you'll never have to go to any anime sites ever again.

### To use `anime_downloader` in your package

This tool can be used as a library. This means you can import it into your own application and search for anime and do many other wonderful things.
See [documentation](https://github.com/vn-ki/anime-downloader/wiki/Package-documentation).

### Development Instructions

See [development instructions](https://github.com/vn-ki/anime-downloader/wiki/Development-Instructions)

---

*Please don't judge me for not paying for anime. I want to support these animation studios, but being a college student, I can't.*

**arigatou gozaimasu**

![arigatou](https://media.giphy.com/media/VUC9YdLSnKuJy/giphy.gif)
