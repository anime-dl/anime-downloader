import pytest

from anime_downloader import util


def test_split_anime():
    anime_list = list(range(20))

    assert len(util.split_anime(anime_list, '1:10')) == 9
