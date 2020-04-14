import pytest

from anime_downloader.sites.animefreak import AnimeFreak
from test_sites.site import configure_httpretty


@pytest.fixture
def anime():
    return AnimeFreak('https://www.animefreak.tv/watch/shingeki-no-kyojin')

configure_httpretty('animefreak')

def test_search():
    ret = AnimeFreak.search('shingeki no kyojin')
    assert len(ret) == 24
    assert ret[2].title == 'Shingeki no Kyojin'


def test_title(anime):
    assert anime.title == 'Shingeki no Kyojin'


def test_length(anime):
    assert len(anime) == 28


def test_streamurl(anime):
    assert anime[0].source().stream_url == 'http://st7.anime1.com/Attack on Titan s1e01_af.mp4?st=orn45gwkj2zr9NbHogG_YA&e=1569695560'
