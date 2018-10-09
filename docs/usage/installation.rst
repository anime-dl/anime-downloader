
Installation
------------

The following are extended installation instructions for Windows and
Linux users. (For windows choco users, scroll to last)

Windows
~~~~~~~

This tool requires python >= 3.3.

-  Go to python windows `downloads section`_. Choose the option
   ``Latest python 3 release``. *Note, not python 2 but python 3*
-  Download and install it like any other application. **Don’t forget to
   select ‘Add Python to PATH’ in the installation screen**
-  After installation open a command prompt and type in the following
   command.

::

   pip install anime-downloader[cloudflare]

-  Enjoy downloading anime.

NOTE: If you want to use ``watch`` you have to do some more steps.
(Trust me, it is work the additional steps) - Download mpv from `here`_.
- Extract the zip and place ``mpv.exe`` in the folder your command
prompt opens. (The path you see when you open command prompt). - Enjoy.
Read documentation for watch to know more.

Windows via ``choco``
~~~~~~~~~~~~~~~~~~~~~

   Contributed by @CodaTheOtaku

.. note::
    make sure you are running the Command Prompt in "Run as Adminstrator" mode

-  Using the Chocolatey Package Manager::

       choco install -y git mpv python3 aria2 nodejs
-  Once these are installed::

        pip3 install -U git+https://github.com/vn-ki/anime-downloader.git#egg=anime-downloader[cloudflare]

-  then the commands to view a show would be::

        anime watch --provider *Insert provider name* --new

Linux
~~~~~

If you are using linux, you most probably already have python installed.

Type ``pip --version`` into your terminal. If it says python2, replace
all the following ``pip`` with ``pip3``.

-  You only need one command.

::

   pip install anime-downloader[cloudflare]

-  Enjoy.
-  You can download mpv with your package manager. You can follow `this
   guide`_, to install it on ubuntu.


Windows via ``choco`` (Method 2)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Contributed by @1ijack

-  Using the `Chocolatey`_ Package manager (via Windows Nuget) to

   -  Install these pre-reqs: `git`_ `python3`_ `aria2`_ `mpv`_
   -  Refresh/Update environment changes (choco ``refreshenv`` command)
   -  clone this repository to
      ``[C:]\Users\[USERNAME]\anime-downloader``
   -  setup/build anime-downloader from
      ``"%userprofile%\anime-downloader"``
   -  run ``anime watch`` command

-  the ``choco install`` command SHOULD be run with an administrator
   privledged ``cmd.exe`` console:

   -  ``[WindowsKey] > "cmd.exe" > [Shift]+[Ctrl]+[Enter] > (Click "Yes")``

   ::

      choco install -y git python3 aria2 mpv

-  the rest of the commands SHOULD be run in an un-privledged/normal
   ``cmd.exe`` console:

   -  ``[WindowsKey] > "cmd.exe" > [Enter]`` \``\` refreshenv git clone
      https://github.com/vn-ki/anime-downloader
      “%userprofile%:raw-latex:`\anime`-downloader” cd /d "

.. _downloads section: https://www.python.org/downloads/windows/
.. _here: https://mpv.srsfckn.biz/
.. _this guide: http://ubuntuhandbook.org/index.php/2017/12/install-mpv-0-28-0-in-ubuntu-18-04-16-04/
.. _Chocolatey: https://chocolatey.org/install
.. _git: https://chocolatey.org/packages/git
.. _python3: https://chocolatey.org/packages/python3
.. _aria2: https://chocolatey.org/packages/aria2
.. _mpv: https://chocolatey.org/packages/mpv
