import click
import sys
import os
import importlib

from anime_downloader.__version__ import __version__

from anime_downloader.config import Config
from anime_downloader import util

echo = click.echo


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
    if not util.check_in_path('aria2c'):
        raise RuntimeError("Aria2 is not in path. Please follow installation instructions: https://github.com/vn-ki/anime-downloader/wiki/Installation")
    util.setup_logger(log_level)


def main():
    try:
        cli()
    except Exception as e:
        if 'DEBUG' in sys.argv:
            raise
        click.echo(click.style('ERROR:', fg='black', bg='red') +
                   ' '+click.style(str(e), fg='red'))
        sys.exit(1)
