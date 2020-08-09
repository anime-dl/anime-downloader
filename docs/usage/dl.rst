``anime dl``
============

.. note::
    **It is recommended to use the external downloader functionality with aria2c because it will be faster than the internal downloader**: Use the argument ``-xd "{aria2}"``

.. note::
    Run ``anime dl --help`` to get the latest cli options.

Search and download
^^^^^^^^^^^^^^^^^^^

-  To search and download all episodes use the following command;

.. code:: bash

   anime dl 'code geass'

To search on kissanime,

.. code:: bash

   anime dl 'code geass' --provider animepahe

Run ``anime dl --help`` for help using the ``dl`` subcommand.

Download directly
^^^^^^^^^^^^^^^^^

-  To download Fullmetal Alchemist: Brotherhood all episodes;

::

   anime dl 'https://animepahe.com/anime/fullmetal-alchemist-brotherhood'

-  To download Fullmetal Alchemist: Brotherhood episode 1;

::

   anime dl 'https://animepahe.com/anime/fullmetal-alchemist-brotherhood' --episodes 1

-  To download Fullmetal Alchemist: Brotherhood episode 1 to 20;

::

   anime dl 'https://animepahe.com/anime/fullmetal-alchemist-brotherhood' --episodes 1:21

-  To get stream url of Fullmetal Alchemist: Brotherhood episode 1;

::

   anime dl 'https://animepahe.com/anime/fullmetal-alchemist-brotherhood' --url --episodes 1

-  To play using vlc. (On windows use path to exe);

::

   anime dl 'https://animepahe.com/anime/fullmetal-alchemist-brotherhood' --play vlc --episodes 1


