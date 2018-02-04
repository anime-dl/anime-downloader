#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='anime-downloader',
    version='1.0',
    packages=find_packages(),
    # py_modules=['anime_downloader'],
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
