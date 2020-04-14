import pytest

from anime_downloader.sites.twistmoe import TwistMoe
from test_sites.site import configure_httpretty


@pytest.fixture
def anime():
    return TwistMoe('https://twist.moe/a/shingeki-no-kyojin/first')

configure_httpretty('twistmoe')

def test_search():
    ret = TwistMoe.search('shingeki no kyojin')
    assert len(ret) == 5
    assert ret[0].title == 'Shingeki no Kyojin'


def test_title(anime):
    assert anime.title == 'shingeki-no-kyojin'


def test_length(anime):
    assert len(anime) == 25


def test_streamurl(anime):
    assert anime[0].source().stream_url == 'https://twist.moe/anime/attackontitan/[Coalgirls]_Shingeki_no_Kyojin_01_(1920x1080_Blu-ray_FLAC)_[AEF12794].mp4'
