"""
# Currently cannot test selenium sites
import pytest

from anime_downloader.sites.kissanime import KissAnime
from test_sites.site import configure_httpretty


@pytest.fixture
def anime():
    return KissAnime('https://kissanime.ru/Anime/Shingeki-no-Kyojin-Dub')

configure_httpretty('kissanime')

def test_search():
    ret = KissAnime.search('shingeki no kyojin')
    assert len(ret) == 16
    assert ret[0].title == 'Attack on Titan (Dub)'


def test_title(anime):
    assert anime.title == 'Attack on Titan (Dub)'


def test_length(anime):
    assert len(anime) == 25


def test_streamurl(anime):
    assert anime[0].source().stream_url == 'https://www432.playercdn.net/86/3/cf1DxUks9XeqNYTLfcQuxg/1569697960/170505/5041aQOsvZ7ekRm.mp4'
"""
