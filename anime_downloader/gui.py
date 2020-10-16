import sys
import time
from PyQt5 import QtWidgets, QtGui, QtCore
from anime_downloader import session, util
from anime_downloader.commands import dl
from anime_downloader.config import Config
from anime_downloader.sites import get_anime_class, ALL_ANIME_SITES, exceptions
import os
import tempfile
import subprocess


class Worker(QtCore.QThread):
    #Worker to run commands on another thread, allowing the GUI not to lock up. Theoretically, any function should be able to be passed to this Worker.
    signal = QtCore.pyqtSignal(int)

    def __init__(self, fn, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @QtCore.pyqtSlot()
    def run(self):
        self.fn(*self.args, **self.kwargs, signal=self.signal)


class Window(QtWidgets.QMainWindow):

    def __init__(self):
        '''
        Initialises the window as well as objects in the window which will always be constant regardless of pages.
        '''
        super().__init__()
        self.updateProgress = None
        self.defaultStyleSheet = self.setStyleSheet("")
        self.setGeometry(50, 50, 400, 400)
        self.setWindowTitle("Anime Downloader")
        self.setWindowIcon(QtGui.QIcon('placeholder.png'))
        self.statusBar()
        menubar = self.menuBar()
        themeMenu = menubar.addMenu('&Themes')
        titles = ['Iggy', 'Arjix', 'Lagrad' ,'Red', 'Default']
        methods = [self.__iggyTheme, self.__arjixTheme, self.__laggyTheme, self.__redTheme, self.__defaultTheme]
        for x, y in zip(titles,methods):
            theme = QtWidgets.QAction(f'&{x} Theme',self)
            theme.triggered.connect(y)
            themeMenu.addAction(theme)

        self.downloadPage()

    def downloadPage(self):
        '''
        Contains all the information for the main download page, this contains all the positioning inputs for the widgets used in this page, as well
        as information regarding connecting signals to later functions.
        '''
        self.animeName = QtWidgets.QLineEdit()
        self.animeEpisodeStart = QtWidgets.QLineEdit()
        self.animeEpisodeEnd = QtWidgets.QLineEdit()
        self.searchButton = QtWidgets.QPushButton('Search')
        self.downloadDirectory = QtWidgets.QLineEdit()
        self.file = QtWidgets.QPushButton('Browse')
        self.providers = QtWidgets.QComboBox()
        self.searchOutput = QtWidgets.QListWidget()
        self.progressBar = QtWidgets.QProgressBar()
        self.playPrompt = QtWidgets.QPushButton('Play')
        self.downloadPrompt = QtWidgets.QPushButton('Download')
        self.cancelButton = QtWidgets.QPushButton('Cancel')

        #Allows for enter to be pressed to get search.
        returnPressedWidgets = [self.animeName, self.animeEpisodeStart, self.animeEpisodeEnd]
        for x in returnPressedWidgets:
            x.returnPressed.connect(self.PrintResults)

        self.PopulateProviders()

        self.animeName.setPlaceholderText('Anime Name:')
        self.animeEpisodeStart.setPlaceholderText('Anime Episode Start:')
        self.animeEpisodeEnd.setPlaceholderText('Anime Episode End:')
        self.downloadDirectory.setPlaceholderText('Download Directory:')
        
        layout = QtWidgets.QVBoxLayout()
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)

        #Adds the widgets to the screen.
        widgetNames = [self.animeName, self.animeEpisodeStart, self.animeEpisodeEnd, self.providers,
                       self.searchButton, self.searchOutput]
        for x in widgetNames:
            layout.addWidget(x)

        horizontalLayout = QtWidgets.QHBoxLayout()
        horizontalLayout.addWidget(self.downloadDirectory)
        horizontalLayout.addWidget(self.file)
        layout.addLayout(horizontalLayout)

        horizontalLayout = QtWidgets.QHBoxLayout()
        horizontalLayout.addWidget(self.downloadPrompt)
        horizontalLayout.addWidget(self.playPrompt)
        layout.addLayout(horizontalLayout)
        layout.addWidget(self.progressBar)
        layout.addWidget(self.cancelButton)

        self.setCentralWidget(central_widget)

        self.searchButton.clicked.connect(self.PrintResults)
        self.file.clicked.connect(self.openFileDialog)
        self.downloadPrompt.clicked.connect(self.download)
        self.playPrompt.clicked.connect(self.play)
        self.cancelButton.clicked.connect(self.cancel)

        self.show()

    def PrintResults(self):
        '''
        This function will return the search outputs for the user to select what anime they want.
        '''
        self.searchOutput.clear()
        cls = get_anime_class(self.providers.currentText())
        searchResults = cls.search(self.animeName.text())
        searchResults = [v.title for v in searchResults]

        self.searchOutput.addItems(searchResults)
        self.searchOutput.repaint()

    def openFileDialog(self):
        '''
        Opens the window selector for users to select what folder they want to download to.
        '''
        filename = QtWidgets.QFileDialog.getExistingDirectory()
        self.downloadDirectory.setText(str(filename) + '/')

    def PopulateProviders(self):
        '''
        Populates the drop down menu for all the providers we have available.
        '''
        sitenames = [v[1] for v in ALL_ANIME_SITES]
        for site in sitenames:
            self.providers.addItem(site)

    def download(self):
        '''
        Contains all the information regarding updating the progress bar as well as passing the downloading to the Worker to download on another thread.
        '''
        self.downloadPrompt.setEnabled(False)
        self.progressBar.setValue(0)
        self.updateProgress = Worker(self.download_episodes)
        self.updateProgress.signal.connect(self.onCountChanged)
        self.updateProgress.start()
        self.updateProgress.finished.connect(self.handleFinished)

    def onCountChanged(self, value):
        '''
        Updates the progress bar.
        '''
        self.progressBar.setValue(value)

    def play(self):
        '''
        Initialises the play button, passes the streaming to another thread.
        '''
        self.progressBar.setValue(0)
        self.updateProgress = Worker(self.play_episodes)
        self.updateProgress.signal.connect(self.onCountChanged)
        self.updateProgress.start()

    def play_episodes(self, signal):
        '''
        Brings all the episodes into a m3u8 playlist for one continuous mpv.
        '''
        self.signal = signal
        animes, anime_title = self.get_animes()

        self.progressBar.setMaximum(len(animes._episode_urls))
        file = self.generate_m3u8(animes)
        p = subprocess.Popen([Config["gui"]["player"], file])
        p.wait()

    def get_animes(self):
        # if nothing is selected it returns -1
        # this makes the choice the first one if nothing is selected from search.
        if self.searchOutput.currentRow() != -1:
            choice = self.searchOutput.currentRow() + 1
        else:
            choice = 1

        start = self.animeEpisodeStart.text(
        ) if self.animeEpisodeStart.text().isnumeric() else 1
        end = int(self.animeEpisodeEnd.text()) + \
            1 if self.animeEpisodeEnd.text().isnumeric() else ''
        episode_range = f'{start}:{end}'

        anime = self.animeName.text()
        provider = self.providers.currentText()
        print(anime, provider, choice)
        anime_url, _ = util.search(anime, provider, choice)

        cls = get_anime_class(anime_url)
        anime = cls(anime_url)
        ep_range = util.parse_episode_range(len(anime), episode_range)
        animes = util.split_anime(anime, ep_range)
        # animes = util.parse_ep_str(anime, episode_range)
        anime_title = anime.title
        # maybe make animes/anime_title self.animes?
        return animes, anime_title

    def get_download_dir(self):
        # Reads the input download dir and if it's empty it uses default.
        download_dir = self.downloadDirectory.text()
        if not download_dir:
            download_dir = Config["dl"]["download_dir"]
        download_dir = os.path.abspath(download_dir)
        return download_dir

    def generate_m3u8(self, animes):
        filepath = tempfile.gettempdir() + '/MirrorList.m3u8'
        text = "#EXTM3U\n"
        for count, episode in enumerate(animes, 1):
            print(count)
            text += f"#EXTINF:,Episode {(episode.ep_no)}\n"
            text += episode.source().stream_url + "\n"
            self.signal.emit(count)

        with open(filepath, "w") as f:
            f.write(text)

        return filepath

    def download_episodes(self, signal):
        self.signal = signal
        animes, anime_title = self.get_animes()
        self.progressBar.setMaximum(len(animes._episode_urls))
        download_dir = self.get_download_dir()

        for count, episode in enumerate(animes, 1):

            ep_no = episode.ep_no
            external = Config["dl"]["external_downloader"]

            if external:
                util.external_download(
                    Config["dl"]["external_downloader"],
                    episode,
                    Config["dl"]["file_format"],
                    Config["dl"]["speed_limit"],
                    path=download_dir
                )

            else:
                episode.download(force=Config["dl"]["force_download"],
                                 path=download_dir,
                                 format=Config["dl"]["file_format"],
                                 range_size=Config["dl"]["chunk_size"]
                                 )

            self.signal.emit(count)
            time.sleep(1)

    def cancel(self):
        if self.updateProgress:
            self.progressBar.setValue(0)
            self.updateProgress.exit()
            print("Process has ended")
            self.updateProgress = None
        else:
            return None

    def handleFinished(self):
        self.downloadPrompt.setEnabled(True)

    def __iggyTheme(self):
        self.setStyleSheet("""
    QMainWindow,
    QAbstractItemView,
    QTabBar::tab
    {
        color: #90EE90;
        background: #000000;
    }
    QPushButton {
        color: #90EE90;
        background-color: #e0558b;
        border-style: double;
        border-color: #323C72;
        border-radius: 2px;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #a88ca2;
    }
    QPushButton:pressed {
        background-color: #838FD0;
        }
    QLineEdit {
        background: #8B008B;
        background-color: #8B008B;
        border-radius: 2px;
        padding: 5px;
        color: #90EE90;
    }
    QComboBox {
        background: #8B008B;
        background-color: #8B008B;
        color: #90EE90;
    }
    QProgressBar{
        color: #90EE90;
    }
    */
    """)

    def __laggyTheme(self):
        self.setStyleSheet("""
    QMainWindow,
    QAbstractItemView,
    QTabBar::tab
    {
        color: white;
        background: #1a2035;
    }
    QPushButton {
        color: white;
        background-color: #5465bf;
        border-style: double;
        border-color: #323C72;
        border-radius: 2px;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #6574C5;
    }
    QPushButton:pressed {
        background-color: #838FD0;
    }
    QLineEdit {
        background: #5A628E;
        color: white;
    }
    QLineEdit:hover {
        background: #6A7199;
    }
    QComboBox {
        color: white;
        background: #5465bf;
        border: 1px solid #323C72;
        border-radius: 3px;
        padding: 4px 5px;
    }
    QComboBox:hover {
        background-color: #6574C5;
    }
    QProgressBar {
        text-align: center;
        color: black;
        border: 2px solid #6574C5;
        border-radius: 3px;
        background: #5A628E;
    }
    QProgressBar::chunk {
        background-color: white;
        width: 20px;
    }
    */
    """)

    def __redTheme(self):
        self.setStyleSheet("""
    QMainWindow,
    QAbstractItemView,
    QTabBar::tab
    {
        color: #FF0000;
        background: #000000;
    }
    QPushButton {
        color: #BB0000;
        background-color: #000000;
        border-style: double;
        border-color: #BB0000;
        border-radius: 2px;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #BB0000;
    }
    QPushButton:pressed {
        background-color: #BB0000;
    }
    QLineEdit {
        background: #000000; 
        border-color: #BB0000;
        color: #FF0000;
    }
    QLineEdit:hover {
        background: #000000;
    }
    QComboBox {
        color: #FF0000;
        background: #000000; 
        border-color: #BB0000;
        border: 1px solid #323C72;
        border-radius: 3px;
        padding: 4px 5px;
    }
    QComboBox:hover {
        background-color: #650000; 
        border-color: #BB0000;
    }
    QProgressBar {
        text-align: center;
        color: black; 
        border-color: #BB0000;
        border: 2px solid #650000;
        border-radius: 3px;
        background: #000000;
    }
    QProgressBar::chunk {
        background-color: #000000;
        width: 20px;
    }
    */
    """)

    def __arjixTheme(self):
        self.setStyleSheet("""
    QMainWindow,
    QAbstractItemView,
    QTabBar::tab
    {
        color: #697041;
        background: #3a192e;
    }
    QPushButton {
        color: #0e1a63;
        background-color: #88d353;
        border-style: double;
        border-color: #320000;
        border-radius: 2px;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #88d353;
    }
    QPushButton:pressed {
        background-color: #88d353;
    }
    QLineEdit {
        background: #88d353;
        color: #0e1a63;
    }
    QLineEdit:hover {
        background: #88d353;
    }
    QComboBox {
        color: #0e1a63;
        background: #88d353;
        border: 1px solid #323C72;
        border-radius: 3px;
        padding: 4px 5px;
    }
    QComboBox:hover {
        background-color: #88d353;
    }
    QProgressBar {
        text-align: center;
        color: #88d353;
        border: 2px solid #0e1a63;
        border-radius: 3px;
        background: #88d353;
    }
    QProgressBar::chunk {
        background-color: #88d353;
        width: 20px;
    }
    */
    """)

    def __defaultTheme(self):
        self.setStyleSheet("")


application = QtWidgets.QApplication(sys.argv)
GUI = Window()
sys.exit(application.exec_())
