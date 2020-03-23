import pytest

from anime_downloader.sites.animesimple import AnimeSimple
from test_sites.site import configure_httpretty


@pytest.fixture
def anime():
    return AnimeSimple('https://animesimple.com/series/1146-attack-on-titan-anime.html')

configure_httpretty('animesimple')

def test_search():
    ret = AnimeSimple.search('shingeki no kyojin')
    assert len(ret) == 9
    assert ret[0].title == 'Attack on Titan'


def test_title(anime):
    assert anime.title == 'Attack on Titan'


def test_length(anime):
    assert len(anime) == 36


# TODO: Test not working on travis. investigate
# def test_streamurl(anime):
#     assert anime[0].source().stream_url == 'https://mp4.sh/v/45cb7341.mp4?hash=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvbXA0LnNoIiwiYXVkIjoiaHR0cHM6XC9cL21wNC5zaCIsImRhdGEiOnsiaWQiOiI0NWNiNzM0MSIsImlwIjoiMTE3LjE5My40My4yMjMifSwiaWF0IjoxNTg0OTYyMjAxLCJleHAiOjE1ODQ5NjIyNjF9.3KaGEIy4Y9sd7SHNW3PJR7C1-1hte_SeSrhKc8_vE98'
