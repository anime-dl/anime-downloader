from anime_downloader import get_anime_class
from anime_downloader.sites.nineanime import NineAnime

import pytest


@pytest.fixture
def anime(anime_url):
    cls = get_anime_class(anime_url)

    return cls(
        anime_url, quality='360p'
    )


def test_length(anime):
    assert len(anime) == 12


def test_title(anime):
    assert anime.title.lower() == 'kochinpa!'


def test_episode(anime):
    episode1 = anime[0]

    assert episode1.title.lower(
    ) == 'tw caffeine chihiro chyuu cthuko ctss damedesuyo dmo eraser evetaku first fff flax hatsuyuki hiryuu kaylith kaitou notsentai p saenaisubs scribbles tsundere watashi yolo kochinpa 01.e.mp4'
    assert episode1.stream_url.endswith('.mp4')


def test_download(anime, tmpdir):
    eps = (anime[0], anime[6], anime[-1])
    for ep in eps:
        ep.download(path=str(tmpdir))


def test_search():
    results = NineAnime.search('dragon ball super')

    assert len(results) == 30
    assert results[0].title.lower() == 'dragon ball super'
