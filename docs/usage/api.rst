Library usage
=============

Anime Downloader also be used as a library.


The following code searches for 'one punch' from twist.moe;

:py:func:`~anime_downloader.sites.init.get_anime_class` can be used to import specific sites using the url one of :py:data:`~anime_downloader.commands.dl.sitenames`.

.. code:: python

    from anime_downloader.sites import get_anime_class

    Twist = get_anime_class('twist.moe')
    search = Twist.search('one punch')
    print(search[0].title)

    # You can directly import twist too
    from anime_downloader.sites.twistmoe import TwistMoe
    anime = TwistMoe(search[0].url)
    print(anime)
    print(len(anime))

    # Get first episodes url
    print(anime[0].source().stream_url)


In the above example, `TwistMoe` is a concrete implementation of :py:class:`anime_downloader.sites.anime.Anime`.
Search results is a list of :py:class:`anime_downloader.sites.anime.SearchResult`.
