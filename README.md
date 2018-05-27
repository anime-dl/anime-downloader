# Anime Downloader

[![Build Status](https://travis-ci.com/vn-ki/anime-downloader.svg?branch=master)](https://travis-ci.com/vn-ki/anime-downloader)
[![codecov](https://codecov.io/gh/vn-ki/anime-downloader/branch/master/graph/badge.svg)](https://codecov.io/gh/vn-ki/anime-downloader)

Download your favourite anime the way you want. Currently only supports 9anime.

## Installation

You can install the stable release from PyPI.
```
$ pip install anime-downloader
```

If you like to live on the bleeding edge, do the following.
``` bash
# Clone this repo
$ git clone https://github.com/vn-ki/anime-downloader.git

# Run setup.py
$ cd anime-downloader
$ python3 setup.py install
```

## Usage

Run `anime-dl --help` for help text.

```
$ anime-dl --help
Usage: anime-dl [OPTIONS] ANIME_URL

  Anime Downloader

  Download your favourite anime.

Options:
  -e, --episodes <int>:<int>      Range of anime you want to download in the
                                  form <start>:<end>
  -p, --save-playlist             If flag is set, saves the stream urls in an
                                  m3u file instead of downloading
  -u, --url                       If flag is set, prints the stream url
                                  instead of downloading
  --play PLAYER                   Streams in the specified player
  --no-download                   Retrieve without downloading
  -q, --quality [360p|480p|720p]  Specify the quality of episode. Default-720p
  -f, --force                     Force downloads even if file exists
  -ll, --log-level [DEBUG|INFO|WARNING|ERROR]
                                  Sets the level of logger
  --help                          Show this message and exit.
```

#### Examples
- To download Fullmetal Alchemist: Brotherhood all episodes
```
anime-dl 'https://9anime.is/watch/fullmetal-alchemist-brotherhood.0r7/j69y93'
```

- To download Fullmetal Alchemist: Brotherhood episode 1
```
anime-dl 'https://9anime.is/watch/fullmetal-alchemist-brotherhood.0r7/j69y93' --episodes 1
```

- To download Fullmetal Alchemist: Brotherhood episode 1 to 20
```
anime-dl 'https://9anime.is/watch/fullmetal-alchemist-brotherhood.0r7/j69y93' --episodes 1:21
```

- To get stream url of Fullmetal Alchemist: Brotherhood episode 1.
```
anime-dl 'https://9anime.is/watch/fullmetal-alchemist-brotherhood.0r7/j69y93' --url --episodes 1
```

- To play using vlc. (On windows use path to exe)
```
anime-dl 'https://9anime.is/watch/fullmetal-alchemist-brotherhood.0r7/j69y93' --play vlc --episodes 1
```


# TODO

- Support for more sites
