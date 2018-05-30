#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()


setup(
    name='anime-downloader',
    version='2.2',
    author='Vishnunarayan K.I.',
    author_email='vishnunarayan6105@gmail.com',
    description='Download your favourite anime',
    packages=find_packages(),
    url='https://github.com/vn-ki/anime-downloader',
    download_url='https://github.com/vn-ki/anime-downloader/archive/2.2.tar.gz',
    keywords=['anime', 'downloader', '9anime', 'download', 'kissanime'],
    install_requires=[
        'bs4',
        'requests',
        'Click',
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points='''
        [console_scripts]
        anime=anime_downloader.cli:cli
    '''
)
