# Anime Downloader

Download your favourite anime the way you want.

## Installation

``` bash
# Clone this repo
$ git clone https://github.com/vn-ki/anime-downloader.git

# Run setup.py
$ cd anime-downloader
$ python3 setup.py install
```

## Usage

Run `anime-dl --help` for help text.

``` bash
$ anime-dl --help
Usage: anime-dl [OPTIONS] ANIME_URL

  Anime Downloader

  Download your favourite anime.

Options:
  --range TEXT  Range of anime you want to download in the form <start>:<end>
  --playlist    If falaf is set, saves the stream urls in an m3u file
  --url         If flag is set, prints the stream url and not download
  --help        Show this message and exit.
```

#### Examples
- To download Fullmetal Alchemist: Brotherhood all episodes
```
anime-dl 'https://9anime.is/watch/fullmetal-alchemist-brotherhood.0r7/j69y93'
```

- To download Fullmetal Alchemist: Brotherhood episode 1
```
anime-dl 'https://9anime.is/watch/fullmetal-alchemist-brotherhood.0r7/j69y93' --range 1
```

- To download Fullmetal Alchemist: Brotherhood episode 1 to 20
```
anime-dl 'https://9anime.is/watch/fullmetal-alchemist-brotherhood.0r7/j69y93' --range 1:21
```

- To get stream url of Fullmetal Alchemist: Brotherhood episode 1. Afterwards the stream can be played by `mpv` or `vlc`.
```
anime-dl 'https://9anime.is/watch/fullmetal-alchemist-brotherhood.0r7/j69y93' --url --range 1
```
