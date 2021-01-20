from anime_downloader.downloader.http_downloader import HTTPDownloader
from anime_downloader.downloader.external_downloader import ExternalDownloader
from anime_downloader.downloader.SmartDL import pySmartDL


def get_downloader(downloader):
    """get_downloader returns the proper downloader class

    TODO: Lazy loading of downloaders
    """
    if downloader == 'http':
        return HTTPDownloader

    elif downloader == 'pySmartDL':
        return pySmartDL

    return ExternalDownloader
