import pytest

from anime_downloader import util


def test_split_anime():
    anime_list = list(range(20))

    assert len(util.split_anime(anime_list, '1:10')) == 9

def test_check_in_path_exists():
    assert util.check_in_path('ls')

def test_check_in_path_not_exists():
    assert not util.check_in_path('someAppI_madeUp') 