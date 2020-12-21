import pytest

from anime_downloader import util
from unittest.mock import Mock

def test_split_anime():
    anime = Mock()
    anime._episode_urls = list(enumerate(range(20)))
    assert len(util.split_anime(anime, '1:10')._episode_urls) == 9

def test_check_in_path_exists():
    assert util.check_in_path('ls')

def test_check_in_path_not_exists():
    assert not util.check_in_path('someAppI_madeUp') 
