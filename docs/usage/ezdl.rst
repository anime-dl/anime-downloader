``anime ezdl``
============

.. note::
    Run ``anime ezdl --help`` to get the latest cli options.

Search and download
^^^^^^^^^^^^^^^^^^^

-  To search and download all episodes use the following command;

.. code:: bash

   anime ezdl 'code geass'


Run ``anime ezdl --help`` for help using the ``ezdl`` subcommand.

Download directly
^^^^^^^^^^^^^^^^^

-  To download Fullmetal Alchemist: Brotherhood all episodes;

::

   anime ezdl 'Fullmetal Alchemist: Brotherhood'

-  To download Fullmetal Alchemist: Brotherhood episode 1 to 20;

::

   anime ezdl 'Fullmetal Alchemist: Brotherhood' --episodes 1:21

-  To download Fullmetal Alchemist: Brotherhood without any auto selection

::

   anime ezdl 'Fullmetal Alchemist: Brotherhood' -r 101

-  To download Fullmetal Alchemist: Brotherhood without any user prompts for providers

::

   anime ezdl 'Fullmetal Alchemist: Brotherhood' -r 0

Understanding ezdl
^^^^^^^^^^^^^^^^^^

Ezdl was made for the primary reason of falling back when one provider fails. Since there's so many sites providers always gets outdated and errors from time to time. 
This *should* also make ezdl more reliable when batch downloading multiple animes.

It searches anilist for the user query, uses that name to search all other providers specified in config (fallback_providers) then prompts you if the search results isn't similar to 
the anilist result. If the result is similar enough it'll auto select that result and start the download immediatly. This auto selection can be configured using -r, --ratio or ratio in config.

**How ratio works**

All search results are compared with the anilist result based on a ratio from 0-100. 0 being no match and 100 being full match.

This means that if you use --ratio 90 it'll only auto select a result if the most similar match has a ratio over 89.

Using --ratio 101 (anything over 100) means that it'll never auto select a match because no matches can go above 100.

Using --ratio 0 means that it will auto select a result regardless of confidence because all results are at least 0.

**Dub/Sub support**

Ezdl supports automatic selection of dub/sub in most providers, based on the providers specific config. 

**Falling back if no results are preferred**

When selecting a provider enter "0" as your choice to fall back to your next configured choice.

**Download metadata**

Using --download-metadata it places a metadata.json file in the download directory with all the anilist metadata. Useful for creating your own libraries.
