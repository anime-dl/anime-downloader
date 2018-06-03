import click
import subprocess
import sys
import os

import logging

from anime_downloader.sites import get_anime_class
from anime_downloader.sites.exceptions import NotFoundError
from anime_downloader.players.mpv import mpv


from anime_downloader import util
from anime_downloader.config import Config
from anime_downloader import watch as _watch

echo = click.echo


@click.group(context_settings=Config.CONTEXT_SETTINGS)
def cli():
    """Anime Downloader

    Download or watch your favourite anime
    """
    pass


# NOTE: Don't put defaults here. Add them to the dict in config
@cli.command()
@click.argument('anime_url')
@click.option('--episodes', '-e', 'episode_range', metavar='<int>:<int>',
              help="Range of anime you want to download in the form <start>:<end>")
@click.option('--url', '-u', type=bool, is_flag=True,
              help="If flag is set, prints the stream url instead of downloading")
@click.option('--play', 'player', metavar='PLAYER',
              help="Streams in the specified player")
@click.option('--skip-download', is_flag=True,
              help="Retrieve without downloading")
@click.option('--download-dir', metavar='PATH',
              help="Specifiy the directory to download to")
@click.option('--quality', '-q', type=click.Choice(['360p', '480p', '720p']),
              help='Specify the quality of episode. Default-720p')
@click.option('--force-download', '-f', is_flag=True,
              help='Force downloads even if file exists')
@click.option('--log-level', '-ll', 'log_level',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              help='Sets the level of logger')
@click.pass_context
def dl(ctx, anime_url, episode_range, url, player, skip_download, quality,
        force_download, log_level, download_dir):
    """ Download the anime using the url or search for it.
    """

    util.setup_logger(log_level)

    if url or player:
        skip_download = True

    cls = get_anime_class(anime_url)

    if not cls:
        anime_url = util.search_and_get_url(anime_url)
        cls = get_anime_class(anime_url)

    try:
        anime = cls(anime_url, quality=quality, path=download_dir)
    except NotFoundError as e:
        echo(e.args[0])
        return
    if episode_range is None:
        episode_range = '1:'+str(len(anime)+1)

    logging.info('Found anime: {}'.format(anime.title))

    if download_dir and not skip_download:
        logging.info('Downloading to {}'.format(os.path.abspath(download_dir)))

    try:
        start, end = [int(x) for x in episode_range.split(':')]
        anime._episodeIds = anime._episodeIds[start-1:end-1]
    except ValueError:
        # Only one episode specified
        anime = [anime[int(episode_range)-1]]

    for episode in anime:
        if url:
            print(episode.stream_url)
            continue

        if player:
            p = subprocess.Popen([player, episode.stream_url])
            p.wait()

        if not skip_download:
            episode.download(force_download)
            print()


@cli.command()
@click.argument('anime_name', required=False)
@click.option('--new', '-n', type=bool, is_flag=True,
              help="Create a new anime to watch")
@click.option('--list', '-l', '_list', type=bool, is_flag=True,
              help="List all animes in watch list")
@click.option('--remove', '-r', 'remove', type=bool, is_flag=True,
              help="Remove the specified anime")
@click.option('--quality', '-q', type=click.Choice(['360p', '480p', '720p']),
              help='Specify the quality of episode.')
@click.option('--log-level', '-ll', 'log_level',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              help='Sets the level of logger', default='INFO')
def watch(anime_name, new, _list, quality, log_level, remove):
    """
    With watch you can keep track of any anime you watch.
    """
    util.setup_logger(log_level)
    watcher = _watch.Watcher()

    if new:
        if anime_name:
            query = anime_name
        else:
            query = click.prompt('Enter a anime name or url', type=str)

        url = util.search_and_get_url(query)

        watcher.new(url)
        sys.exit(0)

    if remove:
        anime = watcher.get(anime_name)
        if anime and click.confirm(
            "Remove '{}'".format(anime.title), abort=True
        ):
            watcher.remove(anime.title)
        else:
            logging.error("Couldn't find '{}'. Use a better search term.".format(anime_name))
            sys.exit(1)
        sys.exit(0)

    if _list:
        watcher.list()
        sys.exit(0)

    if anime_name:
        anime = watcher.get(anime_name)
        if not anime:
            logging.error(
                "Couldn't find '{}'. Use a better search term.".format(anime_name))
            sys.exit(1)

        anime.quality = quality

        logging.info('Found {}'.format(anime.title))
        to_watch = anime[anime.episodes_done:]

        for idx, episode in enumerate(to_watch):

            for tries in range(5):
                logging.info('Playing episode {}'.format(anime.episodes_done+1))
                player = mpv(episode.stream_url)
                returncode = player.play()

                if returncode == mpv.STOP:
                    sys.exit(0)
                elif returncode == mpv.CONNECT_ERR:
                    logging.warning("Couldn't connect. Retrying.")
                    continue
                anime.episodes_done += 1
                watcher.update(anime)
                break
