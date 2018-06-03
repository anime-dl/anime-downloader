# Anime Downloader

[![Build Status](https://travis-ci.com/vn-ki/anime-downloader.svg?branch=master)](https://travis-ci.com/vn-ki/anime-downloader)
[![codecov](https://codecov.io/gh/vn-ki/anime-downloader/branch/master/graph/badge.svg)](https://codecov.io/gh/vn-ki/anime-downloader)
[![PyPI pyversions](https://img.shields.io/badge/python-3.3%2B-blue.svg)](https://pypi.org/project/anime-downloader/)


Ever dreamt about watching anime for free effortlessly without all those unbearable ads? Ever dreamt of downloading your favourite anime for that long trip?

![kawaii](https://media.giphy.com/media/f0yOYF0EtwSVa/giphy.gif)

Yeah. Me too! That's why this tool exists.

## Features

- Download or stream any episode or episode range of any anime.
- Specify the quality you want to stream or download.
- Search available if don't want to copy the url.
- Save yourselves from those malicious ads.

## Supported Sites

- 9anime
- KissAnime [cloudflare]
- KissCartoon [cloudflare]

## Installation

You can install the stable release from PyPI.
```bash
$ pip install anime-downloader
```

To install the dev version
```bash
$ pip install -U git+https://github.com/vn-ki/anime-downloader.git
```
*NOTE: You might have to use pip3 depending on your system*

Cloudflare support is currently only available in master. Use the following command to install with cloudflare support.

```bash
pip install -U git+https://github.com/vn-ki/anime-downloader.git#egg=anime-downloader'[cloudflare]'
```

**IMP**: For cloudflare scraping [cfscrape](https://github.com/Anorov/cloudflare-scrape) is used. It depends on `node-js`. So if you want to use cloudflare, make sure you have node installed.

## Usage

Anime downloader has two sub commands, `dl` and `watch`. `watch` does nothing currently (but when it does, it will be awesome!).

Run `anime dl --help` for help text on `dl` subcommand.

```
$ anime dl --help
Usage: anime dl [OPTIONS] ANIME_URL

  Download the anime using the url or search for it.

Options:
  -e, --episodes <int>:<int>      Range of anime you want to download in the
                                  form <start>:<end>
  -p, --save-playlist             If flag is set, saves the stream urls in an
                                  m3u file instead of downloading
  -u, --url                       If flag is set, prints the stream url
                                  instead of downloading
  --play PLAYER                   Streams in the specified player
  --no-download                   Retrieve without downloading
  --download-dir TEXT             Specifiy the directory to download to
  -q, --quality [360p|480p|720p]  Specify the quality of episode. Default-720p
  -f, --force                     Force downloads even if file exists
  -ll, --log-level [DEBUG|INFO|WARNING|ERROR]
                                  Sets the level of logger
  --help                          Show this message and exit.
```

You can use this tool to search and download or download directly from the url.

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

## TODO

- Support for more sites

*Please don't judge me for not paying for anime. I want to support these animation studios, but being a college student, I can't.*

**arigatou gozaimasu**

![arigatou](https://media.giphy.com/media/VUC9YdLSnKuJy/giphy.gif)
