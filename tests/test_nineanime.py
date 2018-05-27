from anime_downloader.sites.nineanime import NineAnime, NineAnimeEpisode

import pytest

@pytest.fixture
def anime():
    return NineAnime('https://www4.9anime.is/watch/erased.kkw/6n069p')


def test_length(anime):
    assert len(anime) == 12


def test_title(anime):
    assert anime.title.lower() == 'erased'


def test_episode(anime):
    episode1 = anime[0]

    assert episode1.title.lower() == 'kametsu erased 01 bd 1080p hi10 flac 26723cf5.mp4'
    assert episode1.stream_url.endswith('.mp4')


def test_download(anime, tmpdir):
    for ep in anime:
        ep.download(path=str(tmpdir))
