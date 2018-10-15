Writing your own custom site class
**********************************

:code:`anime_downloader` is built with easy extensibility in mind.

Each of the site (in the tool) can roughly be classfied into two.

- Sites which don't use cloudflare DDoS protection. Ex: :py:class:`~anime_downloader.sites.nineanime.NineAnime`
- Sites which use cloudflare DDoS protection. Ex: :py:class:`~anime_downloader.sites.kissanime.KissAnime`

Sites which use cloudflare have the base class :py:class:`~anime_downloader.sites.anime.BaseAnime`. Sites which don't have the base class :py:class:`~anime_downloader.sites.baseanimecf.BaseAnimeCF`.
