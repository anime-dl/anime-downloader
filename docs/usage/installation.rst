
Installation
------------

The following are extended installation instructions for Windows and
Linux users. (For windows choco users, scroll to last)

Installation Instructions for *Mobile operating systems* are at the bottom, the 2 OS's explained are Android and iOS

Windows
~~~~~~~

Please see this video: https://www.youtube.com/watch?v=gC2tctOL5I8 

Automatic Windows install
~~~~~~~~~~~~~~~~~~~~~

Add the following to a file named install.bat and then run it as administrator.

.. code::

   ::This installs choco, as found on https://chocolatey.org/docs/installation
   @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command " [System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"

   choco install -y git mpv python3 aria2 nodejs
   refreshenv && pip3 install -U git+https://github.com/vn-ki/anime-downloader.git && echo Testing providers, the install is done && anime test


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

Android
~~~~~~~

This does not require a rooted device to work

- Install Termux or similar Terminal Emulator

- Install Aria2c via the following command if using Termux ::

   pkg install aria2c
   
- Install Python via the following command if using Termux ::

   pkg install python
   
- Install git via the following command if using Termux ::

   pkg install git
   
- Install Anime-Downloader via the following command after python and git are installed ::

   pip3 install -U git+https://github.com/vn-ki/anime-downloader.git
 
- Enjoy, The normal commands should work the same as on the computer

iOS (Jailbreak Required)
~~~~~~~~~~~~~~~~~~~~~~~~

If you want this project to work on an iOS Device, you will need a jailbroken iPhone. visit r/jailbreak on reddit for the latest jailbreak news and information.

If you already happen to be jailbroken, then great! you are all set to go!

Tinkering May be Required

- Install the following packages from the mcapollo repo (https://mcapollo.github.io/Public/) using your favorite package manager ::

   Aria2, Python@3.7, git, nano (for File editing), A Terminal Emulator (I recommend NewTerm because it has navigation keys)
   
- Open your Terminal Emulator and type in the following command ::

   python3 -m ensurepip
   
- That should set up pip and setuptools

- Next you want to install Anime-Downloader
- To Install Anime-Downloader before the PR which moves an unsupported module into extras follow along, if not, skip to where it has continue in parentheses 

- First you want to clone the repository via this command ::

   git clone https://github.com/vn-ki/anime-downloader.git
   
- next you want change your directory into the cloned repo. To do so, use the following command (it is case sensitive) ::

   cd anime-downloader
   
- next you want to type in this command to start editing the file ::

   nano setup.py
   
- use the arrow keys to navigate to the line that says ::

   'pycryptodome>=3.8.2',
   
- And Delete that line so it looks like this

::image: https://i.imgur.com/0fRiNP6.png

- press the ctrl button then the letter "o", press enter, then press the ctrl button again, then press the letter "X"

- it should exit you back to the command line

- **(continue)** type the following command to install the project ::

   python3 setup.py install
   
- let it run through, then the program should work as it does on the computer
