import click
import sys
import os
import importlib

from anime_downloader.__version__ import __version__

from anime_downloader.config import Config
from anime_downloader import util

echo = click.echo


def check_for_update():
    from pkg_resources import parse_version
    import requests
    import re

    version_file = "https://raw.githubusercontent.com/anime-dl/anime-downloader/master/anime_downloader/__version__.py"
    regex = r"__version__\s*=\s*[\"'](\d+\.\d+\.\d+)[\"']"
    r = requests.get(version_file)

    if not r.ok:
        return

    current_ver = parse_version(__version__)
    remote_ver = parse_version(re.match(regex, r.text).group(1))

    if remote_ver > current_ver:
        print(
            "New version (on GitHub) is available: {} -> {}\n".format(
                current_ver, remote_ver
            )
        )


class CLIClass(click.MultiCommand):

    def list_commands(self, ctx):
        commands_dir = os.path.join(os.path.dirname(__file__), 'commands')
        rv = []
        for filename in os.listdir(commands_dir):
            if filename == '__init__.py':
                continue
            if filename.endswith('.py'):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        command = importlib.import_module(
            "anime_downloader.commands.{}".format(name))
        return command.command


@click.group(cls=CLIClass, context_settings=Config.CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.option(
    '--log-level', '-ll',
    type=click.Choice(['ERROR', 'WARNING', 'INFO', 'DEBUG']),
    default='INFO',
    help="Log Level"
)
def cli(log_level):
    """Anime Downloader

    Download or watch your favourite anime
    """
    util.setup_logger(log_level)
    # if not util.check_in_path('aria2c'):
    #    raise logger.ERROR("Aria2 is not in path. Please follow installation instructions: https://github.com/vn-ki/anime-downloader/wiki/Installation")


def main():
    try:
        check_for_update()
    except Exception:
        pass

    try:
        cli()
    except Exception as e:
        if 'DEBUG' in sys.argv:
            raise
        click.echo(click.style('ERROR:', fg='black', bg='red') +
                   ' ' + click.style(str(e), fg='red'))
        sys.exit(1)
