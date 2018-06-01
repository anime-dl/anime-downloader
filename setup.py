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
        'beautifulsoup4>=4.6.0',
        'requests>=2.18.4',
        'Click>=6.7',
        'fuzzywuzzy[speedup]>=0.16.0',
        'PyYAML>=3.12'
    ],
    extras_require={
        'kissanime': ['cfscrape>=1.9.5']
    },
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points='''
        [console_scripts]
        anime=anime_downloader.cli:cli
    '''
)
