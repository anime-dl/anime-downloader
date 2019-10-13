import pytest

from anime_downloader.sites.animeflv import Animeflv
from test_sites.site import configure_httpretty


@pytest.fixture
def anime():
    return Animeflv('https://animeflv.net/anime/5438/shingeki-no-kyojin-kuinaki-sentaku')

configure_httpretty('animeflv')

def test_search():
    ret = Animeflv.search('shingeki no kyojin')
    assert len(ret) == 11
    assert ret[0].title == 'Shingeki no Kyojin: Kuinaki Sentaku'


def test_title(anime):
    assert anime.title == 'Shingeki no Kyojin: Kuinaki Sentaku'


def test_length(anime):
    assert len(anime) == 2


def test_streamurl(anime):
    assert anime[0].source().stream_url == 'https://storage.googleapis.com/perceptive-ivy-250020.appspot.com/6aedf869dff46901eb393c5e63e77027.mp4?rnd=900821509'
