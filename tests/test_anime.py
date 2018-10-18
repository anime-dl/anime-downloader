from anime_downloader import get_anime_class
from anime_downloader.sites.nineanime import NineAnime

import pytest
import os

@pytest.fixture
def anime(anime_url):
    cls = get_anime_class(anime_url)

    return cls(
        anime_url, quality='480p'
    )


def test_length(anime):
    assert len(anime) == 12


def test_title(anime):
    assert anime.title.lower() in ['kochinpa!', 'kochin pa!']


@pytest.mark.skipif(bool(os.environ.get('CI')), reason="Test fails on ci")
def test_episode(anime):
    episode1 = anime[0]
    assert episode1.stream_url.endswith('.mp4')


@pytest.mark.skipif(bool(os.environ.get('CI')), reason="Test fails on ci")
def test_download(anime, tmpdir):
    eps = (anime[0], anime[6], anime[-1])
    for ep in eps:
        ep.download(path=str(tmpdir))


# def test_search():
#     results = NineAnime.search('dragon ball super')

#     assert len(results) == 30
#     assert results[0].title.lower() in ['dragon ball super', 'dragon ball super movie']
