import click
import subprocess
import sys

import logging

from anime_downloader.sites import get_anime_class
from anime_downloader.sites.exceptions import NotFoundError
from anime_downloader.players.mpv import mpv


from anime_downloader import config, util
from anime_downloader import watch as _watch

echo = click.echo

CONTEXT_SETTINGS = dict(
    default_map=config.DEFAULT_CONFIG
)


@click.group(context_settings=CONTEXT_SETTINGS)
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
@click.option('--save-playlist', '-p', 'playlist', type=bool, is_flag=True,
              help="If flag is set, saves the stream urls in an m3u file instead of downloading")
@click.option('--url', '-u', type=bool, is_flag=True,
              help="If flag is set, prints the stream url instead of downloading")
@click.option('--play', 'player', metavar='PLAYER',
              help="Streams in the specified player")
@click.option('--no-download', is_flag=True,
              help="Retrieve without downloading")
@click.option('--download-dir', help="Specifiy the directory to download to")
@click.option('--quality', '-q', type=click.Choice(['360p', '480p', '720p']),
              help='Specify the quality of episode. Default-720p')
@click.option('--force', '-f', is_flag=True,
              help='Force downloads even if file exists')
@click.option('--log-level', '-ll', 'log_level',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              help='Sets the level of logger')
@click.pass_context
def dl(ctx, anime_url, episode_range, playlist, url, player, no_download, quality,
        force, log_level, download_dir):
    """ Download the anime using the url or search for it.
    """

    util.setup_logger(log_level)
    config.write_default_config()

    cls = get_anime_class(anime_url)

    if not cls:
        anime_url = util.search_and_get_url(anime_url)
        cls = get_anime_class(anime_url)

    try:
        anime = cls(anime_url, quality=quality, path=download_dir)
    except NotFoundError as e:
        echo(e.args[0])
        return

    logging.info('Found anime: {}'.format(anime.title))

    if url or player:
        no_download = True

    if episode_range is None:
        episode_range = '1:'+str(len(anime)+1)

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

        if not no_download:
            episode.download(force)
            print()


@cli.command()
@click.argument('anime_name', required=False)
@click.option('--new', '-n', type=bool, is_flag=True,
              help="Create a new anime to watch")
@click.option('--list', '-l', '_list', type=bool, is_flag=True,
              help="List all animes in watch list")
@click.option('--player', metavar='PLAYER',
              help="Streams in the specified player")
@click.option('--log-level', '-ll', 'log_level',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              help='Sets the level of logger', default='INFO')
def watch(anime_name, new, _list, player, log_level):
    """
    WORK IN PROGRESS: MAY NOT WORK
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

    if _list:
        watcher.list()
        sys.exit(0)

    if anime_name:
        anime = watcher.get(anime_name)

        logging.info('Got {}'.format(anime.title))

        for idx, episode in enumerate(anime[anime.episodes_done:]):
            player = mpv(episode.stream_url)
            returncode = player.play()

            if returncode == mpv.STOP:
                break
            # elif returncode == mpv.CONNECT_ERR:
            #     retry

            watcher.update(anime, idx+1)
