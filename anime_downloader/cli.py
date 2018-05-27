import click
import subprocess

import logging

from anime_downloader.sites.nineanime import NineAnime
from anime_downloader.sites.exceptions import NotFoundError

from . import util

echo = click.echo


@click.command()
@click.argument('anime_url')

@click.option('--episodes', '-e', 'episode_range', metavar='<int>:<int>',
              help="Range of anime you want to download in the form <start>:<end>")

@click.option('--save-playlist', '-p', 'playlist', default=False, type=bool, is_flag=True,
              help="If flag is set, saves the stream urls in an m3u file instead of downloading")

@click.option('--url', '-u', default=False, type=bool, is_flag=True,
              help="If flag is set, prints the stream url instead of downloading")

@click.option('--play', 'player', metavar='PLAYER',
              help="Streams in the specified player")

@click.option('--no-download', default=False, is_flag=True,
              help="Retrieve without downloading")

@click.option('--quality', '-q', type=click.Choice(['360p', '480p', '720p']),
              default='720p',
              help='Specify the quality of episode. Default-720p')

@click.option('--force', '-f', is_flag=True, default=False,
              help='Force downloads even if file exists')

@click.option('--log-level', '-ll', 'log_level',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              default='INFO',
              help='Sets the level of logger')

def cli(anime_url, episode_range, playlist, url, player, no_download, quality,
        force, log_level):
    """ Anime Downloader

        Download your favourite anime.
    """
    util.setup_logger(log_level)

    try:
        anime = NineAnime(anime_url, quality=quality)
    except NotFoundError as e:
        echo(e.args[0])
        return

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
