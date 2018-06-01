from anime_downloader.sites.kissanime import Kissanime

import pytest


@pytest.fixture
def anime():
    return Kissanime(
        'http://kissanime.ru/Anime/Kochin-Pa',
        quality='360p'
    )


def test_length(anime):
    assert len(anime) == 12


def test_title(anime):
    assert anime.title.lower() == ''  # Not getting metadata for now


def test_episode(anime):
    episode1 = anime[0]

    assert episode1.title.lower() == 'senketsusubskochinpa01r859-rh-277.mp4'
    assert episode1.stream_url.endswith('.mp4')


def test_download(anime, tmpdir):
    eps = (anime[0], anime[6], anime[-1])
    for ep in eps:
        ep.download(path=str(tmpdir))
