from anime_downloader import cli

from click.testing import CliRunner


def test_streamurl():
    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        [
            'https://www4.9anime.is/watch/the-seven-deadly-sins-signs-of-holy-war.lxqm/39px7y',
            '--url'
        ]
    )

    assert result.exit_code == 0

    # print(result.output)
    lines = [r.strip() for r in result.output.split('\n')]
    for line in lines:
        if line and not line.startswith('INFO'):
            assert line.endswith('.mp4')


def test_range():
    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        [
            'https://www4.9anime.is/watch/naruto.xx8z/r9k04y',
            '--url',
            '-e',
            '50:55'
        ]
    )

    assert result.exit_code == 0

    lines = [r.strip() for r in result.output.split('\n')]

    for line in lines:
        if line and not line.startswith('INFO'):
            assert line.endswith('.mp4')

    assert len(lines[:-1]) == 5
