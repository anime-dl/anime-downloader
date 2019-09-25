
Installation
------------

The following are extended installation instructions for Windows and
Linux users. (For windows choco users, scroll to last)

Windows via ``choco``
~~~~~~~~~~~~~~~~~~~~~

   Contributed by @CodaTheOtaku

.. note::
    make sure you are running the Command Prompt in "Run as Adminstrator" mode

- Install `Chocolatey`_ Package manager.

-  Using the Chocolatey Package Manager::

       choco install -y git mpv python3 aria2 nodejs
-  Once these are installed::

        pip3 install -U git+https://github.com/vn-ki/anime-downloader.git

-  then the commands to view a show would be::

        anime watch --provider *Insert provider name* --new

Mac
~~~

Anime downloader is avaible from brew.::

    brew install anime-downloader

Linux
~~~~~

If you are using linux, you most probably already have python installed.

Type ``pip --version`` into your terminal. If it says python2, replace
all the following ``pip`` with ``pip3``.

- Install aria2.

-  Install anime-downloader ::

    pip3 install anime-downloader


-  To install master branch::

        pip3 install -U git+https://github.com/vn-ki/anime-downloader.git
-  Enjoy.


.. _downloads section: https://www.python.org/downloads/windows/
.. _here: https://mpv.srsfckn.biz/
.. _Chocolatey: https://chocolatey.org/install
.. _git: https://chocolatey.org/packages/git
.. _python3: https://chocolatey.org/packages/python3
.. _aria2: https://chocolatey.org/packages/aria2
.. _mpv: https://chocolatey.org/packages/mpv
