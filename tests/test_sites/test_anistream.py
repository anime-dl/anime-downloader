import pytest

from anime_downloader.sites.anistream import Anistream
from test_sites.site import configure_httpretty


@pytest.fixture
def anime():
    return Anistream('https://ww5.anistream.xyz/animes/1146-shingeki-no-kyojin')

configure_httpretty('anistream')

def test_search():
    ret = Anistream.search('shingeki%20no%20kyojin')
    assert len(ret) == 9
    assert ret[0].title == 'Shingeki no Kyojin'


def test_title(anime):
    assert anime.title == 'Shingeki no Kyojin'


def test_length(anime):
    assert len(anime) == 36


def test_streamurl(anime):
    assert anime[0].source().stream_url == 'https://mp4.sh/v/45cb7341.mp4?hash=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvbXA0LnNoIiwiYXVkIjoiaHR0cHM6XC9cL21wNC5zaCIsImRhdGEiOnsiaWQiOiI0NWNiNzM0MSIsImlwIjoiMTQuMTM5LjM1LjIzNSJ9LCJpYXQiOjE1Njk2Nzg0MjcsImV4cCI6MTU2OTY3ODQ4N30.dA0wPkLzyJad-ia0v0IkN6YYcguTfKUPUmgNYg7R_oM'
