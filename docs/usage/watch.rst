``watch``
=========
.. note::
    You need `mpv`_ to use this subcommand.

.. figure:: https://thumbs.gfycat.com/FrailSmallGosling-size_restricted.gif
   :alt: gif

   anime watch in action

``anime watch`` can be a all in one solution for your anime needs.
Currently only supports 9anime.

``watch`` will track your progress through an anime and thus make your
life easier.

::

   CONTROLS IN MPV:
   > : Next episode
   < : Previous episode
   q : Quit

::

   $ anime watch --help
   Usage: anime watch [OPTIONS] [ANIME_NAME]

     With watch you can keep track of any anime you watch.

     Available Commands after selection of an anime:
       set    : set episodes_done and title. Ex: set episodes_done=3
       remove : remove selected anime from watch list
       update : Update the episodes of the currrent anime
       watch  : Watch selected anime
       download : Download episodes of selected anime

   Options:
     -n, --new                       Create a new anime to watch
     -l, --list                      List all animes in watch list
     -r, --remove                    Remove the specified anime
     -q, --quality [360p|480p|720p|1080p]
                                     Specify the quality of episode.
     -ll, --log-level [DEBUG|INFO|WARNING|ERROR]
                                     Sets the level of logger
     --help                          Show this message and exit.

``anime watch --new``
---------------------

This command adds an anime to your watch list.

If you run ``anime watch --new``, you will be prompted to enter a search
term. If you already know what to search for, use
``anime watch <search term> --new``. You can then select an anime to be
added to the watch list.

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
\``\` Available Commands after selection of an anime: set : set
episodes_done and title. Ex: set episodes_done=3 remove : remove
selected anime fro

.. _mpv: https://mpv.io/
