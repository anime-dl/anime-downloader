# Anime Downloader

[![Build Status](https://travis-ci.com/vn-ki/anime-downloader.svg?branch=master)](https://travis-ci.com/vn-ki/anime-downloader)
[![codecov](https://codecov.io/gh/vn-ki/anime-downloader/branch/master/graph/badge.svg)](https://codecov.io/gh/vn-ki/anime-downloader)
[![PyPI pyversions](https://img.shields.io/badge/python-3.3%2B-blue.svg)](https://pypi.org/project/anime-downloader/)


Ever dreamt about watching anime for free effortlessly without all those unbearable ads? Ever dreamt of downloading your favourite anime for that long trip?

![kawaii](https://thumbs.gfycat.com/IgnorantYoungDowitcher-size_restricted.gif)

Yeah. Me too! That's why this tool exists.

## Features

- Download or stream any episode or episode range of any anime.
- Specify the quality you want to stream or download.
- Search and download. (Only 9anime)
- Save yourselves from those malicious ads.
- Add any anime to your watch list using `anime watch` and let anime downloader take care of everything for you.
- Configurable using `config.json`. See [doc](https://github.com/vn-ki/anime-downloader/wiki/Config).

## Supported Sites

- 9anime
- KissAnime [cloudflare]
- KissCartoon [cloudflare]
- Gogoanime

## Installation

You can install the stable release from PyPI.
```bash
$ pip install anime-downloader
```

To install with cloudflare support,
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

**IMP**:
- For cloudflare scraping [cfscrape](https://github.com/Anorov/cloudflare-scrape) is used. It depends on `node-js`. So if you want to use cloudflare, make sure you have node installed.
- You might have to use pip3 depending on your system
- If you are using zsh, don't forget to escape `[` and `]` using `\`.

## Usage

Anime downloader has two sub commands, `dl` and `watch`. You can find the documentation in [wiki](https://github.com/vn-ki/anime-downloader/wiki)

- [dl](https://github.com/vn-ki/anime-downloader/wiki/dl-command): `dl` can download anime.
- [watch](https://github.com/vn-ki/anime-downloader/wiki/watch-command): `watch` can manage your anime watching. Needs [mpv](https://mpv.io). With `watch` you'll never have to go to any anime sites ever again.

#### Search and download

- To search and download all episodes.
```bash
anime dl 'code geass'
```
*NOTE: The above command shows the search results (which would fit you're terminal size :innocent:) and you can select the desired result.*

#### Download directly
- To download Fullmetal Alchemist: Brotherhood all episodes
```
anime dl 'https://9anime.is/watch/fullmetal-alchemist-brotherhood.0r7/j69y93'
```

- To download Fullmetal Alchemist: Brotherhood episode 1
```
anime dl 'https://9anime.is/watch/fullmetal-alchemist-brotherhood.0r7/j69y93' --episodes 1
```

- To download Fullmetal Alchemist: Brotherhood episode 1 to 20
```
anime dl 'https://9anime.is/watch/fullmetal-alchemist-brotherhood.0r7/j69y93' --episodes 1:21
```

- To get stream url of Fullmetal Alchemist: Brotherhood episode 1.
```
anime dl 'https://9anime.is/watch/fullmetal-alchemist-brotherhood.0r7/j69y93' --url --episodes 1
```

- To play using vlc. (On windows use path to exe)
```
anime dl 'https://9anime.is/watch/fullmetal-alchemist-brotherhood.0r7/j69y93' --play vlc --episodes 1
```

### To use `anime_downloader` in your package

This tool can be used as a library. This means you can import it into your own application and search for anime and do many other wonderful things.
See [documentation](https://github.com/vn-ki/anime-downloader/blob/master/package_usage.md).

## Development Instructions

``` bash
# Clone this repo
$ git clone https://github.com/vn-ki/anime-downloader.git

# Run setup.py
$ cd anime-downloader
$ pip install -e .
```

*Please don't judge me for not paying for anime. I want to support these animation studios, but being a college student, I can't.*

**arigatou gozaimasu**

![arigatou](https://media.giphy.com/media/VUC9YdLSnKuJy/giphy.gif)
