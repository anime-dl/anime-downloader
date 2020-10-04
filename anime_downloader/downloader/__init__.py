from anime_downloader.downloader.http_downloader import HTTPDownloader
from anime_downloader.downloader.external_downloader import ExternalDownloader
from anime_downloader.downloader.SmartDL import pySmartDL
from anime_downloader.downloader.m3u8_downloader import m3u8
from urllib.parse import urlparse
import requests
from anime_downloader.const import get_random_header


def get_downloader(downloader, source):
    """get_downloader returns the proper downloader class

    TODO: Lazy loading of downloaders
    """

    # This checks the last redirect url for the file extension.
    # If it's m3u8 it uses m3u8-dl.
    with requests.get(source.stream_url,
                      headers={'user-agent': get_random_header()['user-agent'],
                               'Referer': source.referer
                               },
                      stream=True,
                      allow_redirects=True,
                      verify=False
                      ) as r:

        extension = urlparse(r.url).path.split('.')[-1]

    if extension.startswith('m3u'):
        return m3u8

    if downloader == 'http':
        return HTTPDownloader

    elif downloader == 'pySmartDL':
        return pySmartDL

    return ExternalDownloader
