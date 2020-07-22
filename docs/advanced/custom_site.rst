Writing your own custom site class
**********************************

:code:`anime_downloader` is built with easy extensibility in mind.

Each of the sites (in the tool) can roughly be classfied into two catagories;

- Sites which don't use Cloudflare DDoS protection: Ex: :py:class:`~anime_downloader.sites.nineanime.NineAnime`
- Sites which use Cloudflare DDoS protection: Ex: :py:class:`~anime_downloader.sites.kissanime.KissAnime`

All sites have the base class :py:class:`~anime_downloader.sites.anime.Anime`.
There are helper functions defined by :py:func: `anime_downloader.sites.helpers.request.get` and :py:func:`anime_downloader.sites.helpers.request.post`.
You are expected to use these functions to perform any network requests.
There is also a helper function :py:func:`anime_downloader.sites.helpers.request.soupfiy` for making `BeautifulSoup` s out of requests.

All requests are cached. So don't worry about making requests twice.
