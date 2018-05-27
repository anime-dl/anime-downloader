from anime_downloader import cli

import pytest

pytest_plugins = ["pytester"]


@pytest.fixture
def run(testdir):
    def do_run(*args):
        args = ["anime-dl"] + list(args)
        return testdir._run(*args)
    return do_run


def test_streamurl(run):
    result = run(
        'https://www4.9anime.is/watch/the-seven-deadly-sins-signs-of-holy-war.lxqm/39px7y',
        '--url'
    )

    assert result.ret == 0

    for line in result.stdout.lines:
        assert line.endswith('.mp4')


def test_range(run):
    result = run(
        'https://www4.9anime.is/watch/naruto.xx8z/r9k04y',
        '--url',
        '-e',
        '50:55'
    )

    assert result.ret == 0

    for line in result.stdout.lines:
        assert line.endswith('.mp4')

    assert len(result.stdout.lines) == 5
