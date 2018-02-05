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
  --range <int>:<int>         Range of anime you want to download in the form
                              <start>:<end>
  --playlist                  If flag is set, saves the stream urls in an m3u
                              file
  --url                       If flag is set, prints the stream url and not
                              download
  --play PLAYER               Streams in the specified player
  --no-download               Retrieve without downloading
  --quality [360p|480p|720p]  Specify the quality of episode. Default-720p.
  --help                      Show this message and exit.
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

- To get stream url of Fullmetal Alchemist: Brotherhood episode 1.
```
anime-dl 'https://9anime.is/watch/fullmetal-alchemist-brotherhood.0r7/j69y93' --url --range 1
```

- To play using vlc. (On windows use path to exe)
```
anime-dl 'https://9anime.is/watch/fullmetal-alchemist-brotherhood.0r7/j69y93' --play vlc --range 1
```
