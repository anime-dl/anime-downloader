<div align="center">
<img src="https://cdn.discordapp.com/attachments/484717445538643979/564476620401016862/Banner.png">
<br>
<strong><i>A simple yet powerful tool for downloading anime.</i></strong>
<br>
<br>
<a href="https://travis-ci.com/vn-ki/anime-downloader">
<img src="https://img.shields.io/travis/com/vn-ki/anime-downloader.svg?style=for-the-badge&logo=Travis%20CI">
</a>
<a href="https://codecov.io/gh/vn-ki/anime-downloader">
<img src="https://img.shields.io/codecov/c/github/vn-ki/anime-downloader.svg?logo=codecov&style=for-the-badge">
</a>
<a href="https://pypi.org/project/anime-downloader/">
<img src="https://img.shields.io/pypi/v/anime-downloader.svg?logo=python&style=for-the-badge">
</a>
<a href="https://discord.gg/Qn2nWGm">
<img src="https://img.shields.io/discord/483008720167632929.svg?color=%237289DA&label=Discord&logo=Discord&style=for-the-badge">
</a>
<a href="https://anime-downlader.rtfd.io">
<img src="https://img.shields.io/readthedocs/anime-downlader.svg?logo=read%20the%20docs&style=for-the-badge">
</a>
</div>

  
---
  
# Anime Downloader

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
- Configurable using `config.json`. See [documentation](https://github.com/vn-ki/anime-downloader/wiki/Config).
  
## Supported Sites

<!-- [![CircleCI](https://circleci.com/gh/vn-ki/anime-downloader/tree/master.svg?style=svg)](https://circleci.com/gh/vn-ki/anime-downloader/tree/master) -->

- 9anime
- twist.moe
- KissAnime
- KissCartoon
- Gogoanime
- AnimePahe
- Anistream
- Animeflv (Latin)
- itsaturday.com
- Animefreak
- Animeflix
- Masterani.me [cloudlfare] (site shut down**

## Installation

[**Installation instructions***](https://github.com/vn-ki/anime-downloader/wiki/Installation)

If you have trouble installing, see extended installation instructions [here](https://github.com/vn-ki/anime-downloader/wiki/Installation) or join the [discord server](https://discord.gg/Qn2nWGm) for help.

**Note**:
- For cloudflare scraping [cfscrape](https://github.com/Anorov/cloudflare-scrape) is used. It depends on [`node-js`](https://nodejs.org/en/). So if you want to use cloudflare, make sure you have [node-js](https://nodejs.org/en/) installed.
- You might have to use pip3 depending on your system

## Usage 

See [wiki](https://github.com/vn-ki/anime-downloader/wiki).  

Anime downloader has two sub commands, `dl` and `watch`.

- [dl](https://github.com/vn-ki/anime-downloader/wiki/dl-command): `dl` can download anime.
- [watch](https://github.com/vn-ki/anime-downloader/wiki/watch-command): `watch` can manage your anime watch list. Needs [mpv](https://mpv.io). With `watch` you'll never have to go to any anime sites ever again.

**To use `anime_downloader` in your package:**

This tool can be used as a library. This means you can import it into your own application and search for anime and do many other wonderful things.
See [documentation](https://github.com/vn-ki/anime-downloader/wiki/Package-documentation).

**Development Instructions:**

See [development instructions](https://github.com/vn-ki/anime-downloader/wiki/Development-Instructions).

---

*Please don't judge me for not paying for anime. I want to support the anime industry, but being a college student, I can't.*
