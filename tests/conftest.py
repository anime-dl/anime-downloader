import pytest


def pytest_addoption(parser):
    parser.addoption(
        '--anime-url',
        action='store',
        default='https://www4.9anime.is/watch/kochinpa.p6l6/j6ooy2',
        help='URL for (kochinpa!) anime for a specific site'
    )


@pytest.fixture
def anime_url(request):
    return request.config.getoption('--anime-url')
