# Documentation

`anime_downloader` is designed to be used in your own package too.

```python
from anime_downloader import NineAnime

anime = NineAnime('https://www4.9anime.is/watch/dragon-ball-super-dub.r65p', quality='480p')

print(anime.title)
print(len(anime))
```
`quality` can any of `['360p', '480p', '720p']`. If not this line will raise `AnimeDlError`.

```python
ep = anime[0]
```
The type of `ep` is `NineAnimeEpisode`.
```python
print(ep.title)
ep.downloader(path='/home/vn-ki/Downloads/anime/dbs')
```

### Example to download all episodes of dbs.

```python
from anime_downloader import NineAnime

anime = NineAnime('https://www4.9anime.is/watch/dragon-ball-super-dub.r65p', quality='480p')

for ep in anime:
    ep.download()
```
