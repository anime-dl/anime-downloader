import sys
import time
from PyQt5 import QtWidgets, QtGui, QtCore
from anime_downloader import session, util
from anime_downloader.commands import dl
from anime_downloader.config import Config
from anime_downloader.sites import get_anime_class, ALL_ANIME_SITES, exceptions

class Worker(QtCore.QThread):
    signal = QtCore.pyqtSignal(int)
    
    def __init__(self,animes,download_directory):
        QtCore.QThread.__init__(self)
        self.animes = animes
        self.download_directory = download_directory

    @QtCore.pyqtSlot()
    def run(self):
        i = 0 
        for episode in self.animes:
                
                ep_no = episode.ep_no
            
                util.external_download(Config["dl"]["external_downloader"],
                                   episode,
                                   Config["dl"]["file_format"],
                                   Config["dl"]["speed_limit"],
                                   path=self.download_directory)
                
                i += 1
                self.signal.emit(i)
                time.sleep(1)

class Window(QtWidgets.QMainWindow):
    
    
    def __init__(self):
        
        super().__init__()
        self.setGeometry(50,50,400,400)
        self.setWindowTitle("Anime Downloader")
        
        vnTheme = QtWidgets.QAction('&vn-ki Theme', self)        
        iggyTheme = QtWidgets.QAction('&Iggy Theme', self)
        redTheme = QtWidgets.QAction('&Red Theme', self)
        arjixTheme = QtWidgets.QAction('&Arjix Theme', self)
        lagradTheme = QtWidgets.QAction('&Lagrad Theme', self)
        defaultTheme = QtWidgets.QAction('&Default Theme', self)
        self.statusBar()
        menubar = self.menuBar()
        themeMenu = menubar.addMenu('&Themes')
        themeMenu.addAction(vnTheme)
        themeMenu.addAction(lagradTheme)
        themeMenu.addAction(iggyTheme)
        themeMenu.addAction(redTheme)
        themeMenu.addAction(arjixTheme)
        themeMenu.addAction(defaultTheme)
        
        self.downloadPage()
        
 
    def downloadPage(self):
        
        self.animeName = QtWidgets.QLineEdit()
        self.animeEpisodeStart = QtWidgets.QLineEdit()
        self.animeEpisodeEnd = QtWidgets.QLineEdit()
        self.searchButton = QtWidgets.QPushButton('Search')
        self.downloadDirectory = QtWidgets.QLineEdit()
        self.file = QtWidgets.QPushButton('...')
        self.providers = QtWidgets.QComboBox()
        self.searchOutput = QtWidgets.QListWidget()
        self.progressBar = QtWidgets.QProgressBar()
        self.downloadPrompt = QtWidgets.QPushButton('Download')
        
        self.PopulateProviders()
        
        self.animeName.setPlaceholderText('Anime Name:')
        self.animeEpisodeStart.setPlaceholderText('Anime Episode Start:')
        self.animeEpisodeEnd.setPlaceholderText('Anime Episode End:')
        self.downloadDirectory.setPlaceholderText('Download Directory:')
        
        layout = QtWidgets.QVBoxLayout()
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        
        layout.addWidget(self.animeName)
        layout.addWidget(self.animeEpisodeStart)
        layout.addWidget(self.animeEpisodeEnd)
        layout.addWidget(self.providers)
        layout.addWidget(self.searchButton)
        layout.addWidget(self.searchOutput)
        layout.addWidget(self.downloadDirectory)
        layout.addWidget(self.file)
        layout.addWidget(self.downloadPrompt)
        layout.addWidget(self.progressBar)
         
        self.setCentralWidget(central_widget)
        
        self.searchButton.clicked.connect(self.PrintResults)
        self.file.clicked.connect(self.openFileDialog)
        self.downloadPrompt.clicked.connect(self.download)

        self.show()
    
    def PrintResults(self):

        self.searchOutput.clear()
        cls = get_anime_class(self.providers.currentText())
        searchResults = cls.search(self.animeName.text())
        searchResults = [v.title for v in searchResults]
          
        self.searchOutput.addItems(searchResults)
        self.searchOutput.repaint()
    
    def openFileDialog(self):
        
        filename = QtWidgets.QFileDialog.getExistingDirectory()
        self.downloadDirectory.setText(str(filename) + '/')
        
    def PopulateProviders(self):
        
        sitenames = [v[1] for v in ALL_ANIME_SITES]
        for site in sitenames:
            self.providers.addItem(site)
    
    def download(self):
        
        choice = self.searchOutput.currentRow() + 1
        episode_range = f'{self.animeEpisodeStart.text()}:{self.animeEpisodeEnd.text()}'
        anime = self.animeName.text()
        download_directory = self.downloadDirectory.text()
        provider = self.providers.currentText()
        
        anime_url, _ = util.search(anime, provider, choice)
        
        cls = get_anime_class(anime_url)
        
        anime = cls(anime_url)
        animes = util.parse_ep_str(anime, episode_range)
        anime_title = anime.title
        self.progressBar.setMaximum(len(animes))
        i = 1
        
        self.updateProgress = Worker(animes,download_directory)
        self.updateProgress.signal.connect(self.onCountChanged)
        self.updateProgress.start()
        
    def onCountChanged(self,value):
        
        self.progressBar.setValue(value)

        
application = QtWidgets.QApplication(sys.argv)
GUI = Window()
sys.exit(application.exec_())
