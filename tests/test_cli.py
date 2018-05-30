from anime_downloader import cli

from click.testing import CliRunner

import os


def assert_lines(lines, test_string):
    for line in lines:
        if line and not line.startswith('INFO'):
            assert test_string in line


def test_streamurl():
    runner = CliRunner()
    result = runner.invoke(
        cli.dl,
        [
            'https://www4.9anime.is/watch/the-seven-deadly-sins-signs-of-holy-war.lxqm/39px7y',
            '--url'
        ]
    )

    assert result.exit_code == 0

    lines = [r.strip() for r in result.output.split('\n')]

    assert_lines(lines, '.mp4')


def test_download(tmpdir):
    runner = CliRunner()
    result = runner.invoke(
        cli.dl,
        [
            'https://www4.9anime.is/watch/kochinpa.p6l6/j6ooy2',
            '--download-dir',
            str(tmpdir),
        ]
    )

    assert result.exit_code == 0

    length = len(tmpdir.listdir())

    assert length == 12


def test_range():
    runner = CliRunner()
    result = runner.invoke(
        cli.dl,
        [
            'https://www4.9anime.is/watch/naruto.xx8z/r9k04y',
            '--url',
            '-e',
            '50:55',
            '-q',
            '360p'
        ]
    )

    assert result.exit_code == 0

    lines = [r.strip() for r in result.output.split('\n')]

    assert_lines(lines, '.mp4')

    assert len(lines[:-1]) == 5


def test_search():
    runner = CliRunner()
    result = runner.invoke(
        cli.dl,
        [
            'dragon ball super',
            '--url',
            '-e',
            '50:55'
        ],
        input='1\n'
    )

    # Currently only checking for exit codes
    assert result.exit_code == 0

    result2 = runner.invoke(
        cli.dl,
        [
            'dragon ball super',
            '--url',
            '-e',
            '50:55'
        ],
        input='77\n'
    )

    assert result2.exit_code == 1
