``watch``
=========
.. note::
    You need `mpv`_ to use this subcommand currently. Work is being done to add VLC as a player also, but will have reduced functionality.

.. figure:: https://thumbs.gfycat.com/FrailSmallGosling-size_restricted.gif
   :alt: gif

   anime watch in action

``anime watch`` can be a all in one solution for your anime needs. Anime watch contains exactly the same providers used in anime dl so you will not be missing anything!

``watch`` will locally track your progress with an anime list making your time with anime watch easy and enjoyable. Anime lists from MyAnimeList can also be imported into your list, so you need not worry about losing a complete tracker!

.. figure:: https://media.giphy.com/media/RKNArLOzM2jUjkXNJu/giphy.gif
   :alt: mp4
   
   Revamped watch command with an imported MyAnimeList list!!
::

   CONTROLS IN MPV:
   > : Next episode
   < : Previous episode
   q : Quit

::

   $ anime watch --help
   Usage: anime watch [OPTIONS] [ANIME_NAME]

     With watch you can keep track of any anime you watch.
     
     Using anime watch without any options:
        Using anime watch without any options will return the complete tracking list. Allowing for quick access to the list.
     
     Available Commands inside a list:
        swap  : Swap the list
        add   : Add new anime
     
     Available Commands after selection of an anime:
       set    : Set episodes_done, provider,title, anime_status and stars. Ex: set episodes_done=3
       remove : Remove selected anime from watch list.
       update : Update the episodes of the currrent anime, brilliant for currently airing series.
       watch  : Watch selected anime.
       download : Download episodes of selected anime.
       back : Return back to the list.

   Options:
     -n, --new                       Add a new entry to the list.
     -l, --list  [all,completed,watching,dropped,planned]
                                     Return a list of the anime from the tracker, sorted by anime_status. 
     -r, --remove                    Remove a specified anime from the list.
     --mal_import [FILEPATH]                    Give a .xml MAL file to populate the list with MAL.
     -q, --quality [360p|480p|720p|1080p]
                                     Specify the quality of episodes.
     -ll, --log-level [DEBUG|INFO|WARNING|ERROR]
                                     Sets the level of logger.
     --help                          Show this message and exit.

``anime watch --new``
---------------------

This command adds an anime to your watch list.

If you run ``anime watch --new``, you will be prompted to enter a search
term. If you already know what to search for, use
``anime watch <search term> --new``. You can then select an anime to be
added to the watch list.

If you are familiar with the dl side of anime downloader then you can also specify your choice of provider at this point with the ``--provider`` flag.
::

   $ anime watch 'code geass' --new
    1: Code Geass: Nunnally in Wonderland          OVA
    2: Code Geass: Fukkatsu no Lelouch             Preview | Ep 2 Previ
    3: Code Geass: Lelouch of the Rebellion (Du    DUB | Ep 25/25
    4: Code Geass: Hangyaku no Lelouch Recaps      Special | Ep 2/2
    5: Code Geass: Lelouch of the Rebellion R2     Ep 25/25
    6: Code Geass: Hangyaku no Lelouch III - Ou    Preview
    7: Code Geass: Hangyaku no Lelouch I - Koud    Movie
    8: Code Geass: Hangyaku no Lelouch II - Han    Preview
    9: Code Geass: Lelouch of the Rebellion        Ep 25/25
   10: Code Geass: Lelouch of the Rebellion R2     DUB | Ep 25/25

   Enter the anime no:  [1]: 9
   INFO:Selected Code Geass: Lelouch of the Rebellion
   INFO:Extracting episode info from page
   INFO:Added Code Geass: Lelouch of the Rebellion to watch list.

``anime watch --list``
----------------------

This command lists your watch list.

::

   $ anime watch --list
    SlNo |                Name                 |   Eps    |    Type
   -----------------------------------------------------------------
       1 | Code Geass: Lelouch of the Rebellio |    0/25  | TV Series

You can select an anime from this list and perform an action on it.
\``\` 

Once you select an anime from the table a new enviroment for you to use appears, this has the following options;

- set: Update information about the anime on the list. Episodes, title and provider changes go here.

- remove: Remove an anime from the list.

- update: Update the episode range of the anime.

- watch: Watch an episode of the anime and then return back to this enviroment.

- download: Download an episode of the anime.

- back: Return back to the list

.. _mpv: https://mpv.io/
