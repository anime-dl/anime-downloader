<div align="center">
<img src="https://i.imgur.com/7De34Nh.png">
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
- Have a locally stored anime list to track your progress and stream anime using the watch command.
- Import your MAL anime list to the local anime list.
- Specify the quality you want to stream or download.
- Search and download.
- Save yourselves from those malicious ads.
- Download using external downloader ([aria2](https://aria2.github.io/) recommended).
- Configurable using `config.json`. See [documentation](https://anime-downlader.readthedocs.io/en/latest/usage/config.html).

## Supported Operating Systems:
- Windows
- Mac OS
- Linux
- Android
- iOS (requires Jailbreak and some tinkering)
  * Instructions for Mobile Operating Systems can be found in the [Installation Documentation Page](https://anime-downlader.readthedocs.io/en/latest/usage/installation.html)

## Supported Sites
**Details about the sites can be found in [FAQ](https://github.com/vn-ki/anime-downloader/wiki/FAQ)**

- 4Anime
- 9Anime
- a2zanime
- Anistream
- AnimeOnline360
- Animeflix
- Animefreak
- animeout
- Animeflv
- AnimeKisa
- Animesimple
- Animerush
- Animedaisuki
- Animixplay
- Animevibe
- Dbanimes
- Darkanime
- DreamAnime
- Erai-Raws
- Gogoanime
- GurminderBoparai (AnimeChameleon)
- HorribleSubs
- itsaturday
- Justdubs
- Kickassanime
- Kissanimefree
- Kissanime - requires Selenium
- Kisscartoon - requires Selenium
- Nyaa.si
- RyuAnime
- twist.moe - requires Node.js
- Watchmovie
- Yify
- Vostfree
- Voiranime
- Vidstream

Sites that require Selenium **DO NOT** and **WILL NOT** work on mobile operating systems

Twist.moe **DOES NOT** work and **WILL NOT** work on iOS, a specific Python module that is required for twist.moe is not supported on iOS and cannot be installed.

## Installation

[**Installation instructions***](https://anime-downlader.readthedocs.io/en/latest/usage/installation.html)

If you have trouble installing, see extended installation instructions [here](https://anime-downlader.readthedocs.io/en/latest/usage/installation.html) or join the [discord server](https://discord.gg/Qn2nWGm) for help.

**Note**:
- For Cloudflare scraping either [cfscrape](https://github.com/Anorov/cloudflare-scrape) or [selenium](https://www.selenium.dev/) is used. [Cfscrape](https://github.com/Anorov/cloudflare-scrape) depends on [`node-js`](https://nodejs.org/en/) and [selenium](https://www.selenium.dev/) utilizes an automated invisible instance of a browser (chrome/firefox). So, if you want to use Cloudflare enabled sites, make sure you have [node-js](https://nodejs.org/en/) and a [webdriver](https://www.selenium.dev/selenium/docs/api/py/index.html#drivers) installed.
- You might have to use pip3 depending on your system

## Usage

See [docs](https://anime-downlader.readthedocs.io/en/latest/usage/dl.html).

Anime Downloader has two sub-commands, `dl` and `watch`.

- [dl](https://anime-downlader.readthedocs.io/en/latest/usage/dl.html): `dl` can download anime.
- [watch](https://anime-downlader.readthedocs.io/en/latest/usage/watch.html): `watch` can manage your anime watch list. Needs [mpv](https://mpv.io).

**To use `anime_downloader` in your package:**

This tool can be used as a library. This means you can import it into your own applications and search for anime and do many other wonderful things.
See [documentation](https://anime-downlader.readthedocs.io/en/latest/usage/api.html).

**Development Instructions:**

See [development instructions](https://anime-downlader.readthedocs.io/en/latest/advanced/custom_site.html).

## Related Projects

- [adl](https://github.com/RaitaroH/adl) - a command-line tool for watching anime that makes use of anime-downloader.
- [Cloudstream](https://github.com/LagradOst/CloudStream-2) - mobile gui for pirating anime and movies.

---

*Please don't judge me for not paying for anime. I want to support the anime industry, but being a college student, I can't.*
