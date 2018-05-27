import click
import subprocess
from anime_downloader.sites.nineanime import NineAnime
from anime_downloader.sites.anime import NotFoundError

echo = click.echo


@click.command()
@click.argument('anime_url')
@click.option('--range', 'range_', metavar='<int>:<int>',
              help="Range of anime you want to download in the form <start>:<end>")
@click.option('--playlist', default=False, type=bool, is_flag=True,
              help="If flag is set, saves the stream urls in an m3u file")
@click.option('--url', default=False, type=bool, is_flag=True,
              help="If flag is set, prints the stream url and not download")
@click.option('--play', 'player', metavar='PLAYER',
              help="Streams in the specified player")
@click.option('--no-download', default=False, is_flag=True,
              help="Retrieve without downloading")
@click.option('--quality', type=click.Choice(['360p', '480p', '720p']),
              default='720p',
              help='Specify the quality of episode. Default-720p')
@click.option('--force', is_flag=True, default=False,
              help='Force downloads even if file exists')
def cli(anime_url, range_, playlist, url, player, no_download, quality, force):
    """ Anime Downloader

        Download your favourite anime.
    """
    try:
        anime = NineAnime(anime_url, quality=quality,
                          callback=lambda message: print('[INFO] '+message))
    except NotFoundError as e:
        echo(e.args[0])
        return

    if url or player:
        no_download = True

    if range is None:
        range_ = '1:'+str(len(anime)+1)

    try:
        start, end = [int(x) for x in range_.split(':')]
        anime._episodeIds = anime._episodeIds[start-1:end-1]
    except ValueError:
        # Only one episode specified
        anime = [anime[int(range_)-1]]

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
