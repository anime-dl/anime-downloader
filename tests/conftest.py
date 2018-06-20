import pytest


def pytest_addoption(parser):
    parser.addoption(
        '--anime-site',
        action='store',
        default='gogoanime',
        help='A specific anime site'
    )


@pytest.fixture
def anime_url(request):
    site = request.config.getoption('--anime-site')

    if site == 'nineanime':
        return 'https://www4.9anime.is/watch/kochinpa.p6l6/j6ooy2'
    elif site == 'kissanime':
        return 'http://kissanime.ru/Anime/Kochin-Pa'
    elif site == 'gogoanime':
        return 'https://www2.gogoanime.se/category/kochin-pa-'
