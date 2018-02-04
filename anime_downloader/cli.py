import click
from .anime import Anime

echo = click.echo


@click.command()
@click.argument('anime_url')
@click.option('--range', help="Range of anime you want to"
              " download in the form <start>:<end>")
@click.option('--playlist', default=False, help="If falaf is set, saves the"
              " stream urls in an m3u file", type=bool, is_flag=True)
@click.option('--url', default=False, help="If flag is set, prints the"
              " stream url and not download", type=bool, is_flag=True)
def cli(anime_url, range, playlist, url):
    """ Anime Downloader

        Download your favourite anime.
    """
    anime = Anime(anime_url)

    if range is None:
        range = '1:'+str(len(anime)+1)

    try:
        start, end = [int(x) for x in range.split(':')]
        anime._episodeIds = anime._episodeIds[start-1:end-1]
    except ValueError:
        # Only one episode specified
        anime = [anime[int(range)-1]]

    for episode in anime:
        if url:
            print(episode.stream_url)
            continue

        episode.download()
