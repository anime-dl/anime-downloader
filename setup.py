#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='anime-downloader',
    version='1.1',
    author='Vishnunarayan K.I.',
    author_email='vishnunarayan6105@gmail.com',
    description='Download your favourite anime',
    packages=find_packages(),
    url='https://github.com/vn-ki/anime-downloader',
    download_url='https://github.com/vn-ki/anime-downloader/archive/1.1.tar.gz',
    keywords=['anime', 'downloader'],
    install_requires=[
        'bs4',
        'requests',
        'Click',
    ],
    entry_points='''
        [console_scripts]
        anime-dl=anime_downloader.cli:cli
    '''
)
