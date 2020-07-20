
Installation
------------
This document provides complete installation instructions for the following systems: Windows, Mac, Linux, Android, iOS and Windows Choco. Please contact the dev team if you find any errors or inconsistencies in this document. 

Windows
~~~~~~~

Please see this video: https://www.youtube.com/watch?v=gC2tctOL5I8 

Automatic Windows install
~~~~~~~~~~~~~~~~~~~~~

Add the following to a file named install.bat and then run it as Administrator;

.. code::

   ::This installs choco, as found on https://chocolatey.org/docs/installation
   @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command " [System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"

   choco install -y git mpv python3 aria2 nodejs
   refreshenv && pip3 install -U git+https://github.com/vn-ki/anime-downloader.git && echo Testing providers, the install is done && anime test


Windows via ``choco``
~~~~~~~~~~~~~~~~~~~~~

 Contributed by @CodaTheOtaku
**NOTE** Ensure the Command Prompt (cmd) is being ran as Administrator.

- Install `Chocolatey`_ Package manager.

-  Using the Chocolatey Package Manager; ::

       choco install -y git mpv python3 aria2 nodejs
-  Once these are installed; ::

        pip3 install -U git+https://github.com/vn-ki/anime-downloader.git

-  Then, the commands to view a show would be; ::

        anime dl "showname" --provider *Insert provider name* --new --play *mpv or vlc*
        

Mac
~~~

Anime-Downloader is available from brew via the following command; ::

    brew install anime-downloader

Linux
~~~~~

If you are using Linux, Python is probably already installed.
Type ``pip --version`` into your terminal. If the command returns python2, replace
all the following ``pip`` with ``pip3``.

- Install aria2.

-  Install Anime-Downloader via the following command; ::

    pip3 install anime-downloader


-  To install the bleeding-edge version of Anime-Downloader use this alternative command;:

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

This does not require a rooted device to work.

- Install Termux or similar Terminal Emulator.

- Install Aria2c via the following command if using Termux; ::

   pkg install aria2c
   
- Install Python via the following command if using Termux; ::

   pkg install python
   
- Install git via the following command if using Termux; ::

   pkg install git
   
- Install Anime-Downloader via the following command after python and git are installed; ::

   pip3 install -U git+https://github.com/vn-ki/anime-downloader.git
 
- The usage commands should now match the commands used on PC.

iOS (Jailbreak Required)
~~~~~~~~~~~~~~~~~~~~~~~~

 A jailbroken iPhone is required. Visit r/jailbreak on Reddit for the latest jailbreak news and information.

Tinkering May be Required.

- Install the following packages from the mcapollo repo (https://mcapollo.github.io/Public/) using your favorite package manager; ::

   Aria2, Python@3.7, git, nano (for File editing) and a Terminal Emulator (NewTerm is an example of this).
   
- Open your Terminal Emulator and type in the following command; ::

   python3 -m ensurepip
   
- Pip and setuptools should now be installed.
The following steps install Anime-Downloader;
- To install Anime-Downloader before the PR which moves an unsupported module into extras follow along, if not, skip to **(continue)**; 

- Firstly, clone the repository via this command; ::

   git clone https://github.com/vn-ki/anime-downloader.git
   
- Next, change your directory into the cloned repo. To do so, use the following case-sensitive command; ::

   cd anime-downloader
   
- Following this, type in the following command to start editing the file; ::

   nano setup.py
   
- Navigate to the following line using the arrow keys; ::

   'pycryptodome>=3.8.2',
   
- Delete the highlighted line as to match the image below;

:image: https://i.imgur.com/0fRiNP6.png

- Press ctrl+o then enter then press ctrl+X.

- If all the steps were performed correctly then you should be back to the command line.

- **(continue)** Type the following command to install the project; ::

   python3 setup.py install
   
- Wait for the line to finish, then the program functions the same as the PC version.
