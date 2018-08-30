import click
import sys
import os

import logging

from anime_downloader.sites import get_anime_class
from anime_downloader.players.mpv import mpv
from anime_downloader.__version__ import __version__

from anime_downloader import util
from anime_downloader.config import Config
from anime_downloader import watch as _watch

echo = click.echo


@click.group(context_settings=Config.CONTEXT_SETTINGS)
@click.version_option(version=__version__)
def cli():
    """Anime Downloader

    Download or watch your favourite anime
    """
    pass


# NOTE: Don't put defaults here. Add them to the dict in config
@cli.command()
@click.argument('anime_url')
@click.option(
    '--episodes', '-e', 'episode_range', metavar='<int>:<int>',
    help="Range of anime you want to download in the form <start>:<end>")
@click.option(
    '--url', '-u', type=bool, is_flag=True,
    help="If flag is set, prints the stream url instead of downloading")
@click.option(
    '--play', 'player', metavar='PLAYER',
    help="Streams in the specified player")
@click.option(
    '--skip-download', is_flag=True,
    help="Retrieve without downloading")
@click.option(
    '--download-dir', metavar='PATH',
    help="Specifiy the directory to download to")
@click.option(
    '--quality', '-q', type=click.Choice(['360p', '480p', '720p', '1080p']),
    help='Specify the quality of episode. Default-720p')
@click.option(
    '--fallback-qualities', '-fq', cls=util.ClickListOption,
    help='Specifiy the order of fallback qualities as a list.')
@click.option(
    '--force-download', '-f', is_flag=True,
    help='Force downloads even if file exists')
@click.option(
    '--log-level', '-ll', 'log_level',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
    help='Sets the level of logger')
@click.option(
    '--file-format', '-ff', default='{anime_title}/{anime_title}_{ep_no}',
    help='Format for how the files to be downloaded be named.',
    metavar='FORMAT STRING'
)
@click.option(
    '--provider',
    help='The anime provider (website) for search.',
    type=click.Choice(['9anime', 'kissanime', 'twist.moe', 'animepahe', 'kisscartoon'])
)
@click.option(
    '--external-downloader', '-xd',
    help='Use an external downloader command to download. '
         'Use "{aria2}" to use aria2 as downloader. See github wiki.',
    metavar='DOWNLOAD COMMAND'
)
@click.option(
    '--chunk-size',
    help='Chunk size for downloading in chunks(in MB). Use this if you '
         'experience throttling.',
    type=int
)
@click.pass_context
def dl(ctx, anime_url, episode_range, url, player, skip_download, quality,
       force_download, log_level, download_dir, file_format, provider,
       external_downloader, chunk_size, fallback_qualities):
    """ Download the anime using the url or search for it.
    """

    util.setup_logger(log_level)
    util.print_info(__version__)

    cls = get_anime_class(anime_url)

    if not cls:
        anime_url = util.search(anime_url, provider)
        cls = get_anime_class(anime_url)

    try:
        anime = cls(anime_url, quality=quality,
                    fallback_qualities=fallback_qualities)
    except Exception as e:
        if log_level != 'DEBUG':
            echo(click.style(str(e), fg='red'))
        else:
            raise
        return

    # TODO: Refractor this somewhere else. (util?)
    if episode_range is None:
        episode_range = '1:'
    if episode_range.endswith(':'):
        episode_range += str(len(anime)+1)
    if episode_range.startswith(':'):
        episode_range = '1' + episode_range

    logging.info('Found anime: {}'.format(anime.title))

    anime = util.split_anime(anime, episode_range)

    if url or player:
        skip_download = True

    if download_dir and not skip_download:
        logging.info('Downloading to {}'.format(os.path.abspath(download_dir)))

    for episode in anime:
        if url:
            util.print_episodeurl(episode)

        if player:
            util.play_episode(episode, player=player)

        if not skip_download:
            if external_downloader:
                logging.info('Downloading episode {} of {}'.format(
                    episode.ep_no, anime.title)
                )
                util.external_download(external_downloader, episode,
                                       file_format, path=download_dir)
                continue
            if chunk_size is not None:
                chunk_size *= 1e6
                chunk_size = int(chunk_size)
            episode.download(force=force_download,
                             path=download_dir,
                             format=file_format,
                             range_size=chunk_size)
            print()


@cli.command()
@click.argument('anime_name', required=False)
@click.option(
    '--new', '-n', type=bool, is_flag=True,
    help="Create a new anime to watch")
@click.option(
    '--list', '-l', '_list', type=bool, is_flag=True,
    help="List all animes in watch list")
@click.option(
    '--remove', '-r', 'remove', type=bool, is_flag=True,
    help="Remove the specified anime")
@click.option(
    '--update-all', '-u', 'update_all', type=bool, is_flag=True,
    help="Update the episodes of all anime in your list"
)
@click.option(
    '--quality', '-q', type=click.Choice(['360p', '480p', '720p', '1080p']),
    help='Specify the quality of episode.')
@click.option(
    '--download-dir', metavar='PATH',
    help="Specify the directory to download to")
@click.option(
    '--provider',
    help='The anime provider (website) for search.',
    type=click.Choice(['9anime', 'kissanime', 'twist.moe', 'kisscartoon'])
)

@click.option(
    '--log-level', '-ll', 'log_level',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
    help='Sets the level of logger', default='INFO')
def watch(anime_name, new, update_all, _list, quality, log_level, remove,
          download_dir, provider):
    """
    With watch you can keep track of any anime you watch.

    Available Commands after selection of an anime:\n
    set        : set episodes_done, provider and title.
                 Ex: set episodes_done=3\n
    remove     : remove selected anime from watch list\n
    update     : Update the episodes of the currrent anime\n
    watch      : Watch selected anime\n
    download   : Download episodes of selected anime
    """
    util.setup_logger(log_level)
    util.print_info(__version__)

    watcher = _watch.Watcher()

    if new:
        if anime_name:
            query = anime_name
        else:
            query = click.prompt('Enter a anime name or url', type=str)

        url = util.search(query, provider)

        watcher.new(url)
        sys.exit(0)

    if remove:
        anime = watcher.get(anime_name)
        if anime and click.confirm(
            "Remove '{}'".format(anime.title), abort=True
        ):
            watcher.remove(anime)
        else:
            logging.error("Couldn't find '{}'. "
                          "Use a better search term.".format(anime_name))
            sys.exit(1)
        sys.exit(0)

    if update_all:
        animes = watcher.anime_list()
        for anime in animes:
            watcher.update_anime(anime)

    if _list:
        list_animes(watcher, quality, download_dir)
        sys.exit(0)

    if anime_name:
        anime = watcher.get(anime_name)
        if not anime:
            logging.error(
                "Couldn't find '{}'."
                "Use a better search term.".format(anime_name))
            sys.exit(1)

        anime.quality = quality

        logging.info('Found {}'.format(anime.title))
        watch_anime(watcher, anime)


def list_animes(watcher, quality, download_dir):
    watcher.list()
    inp = click.prompt('Select an anime', default=1)
    try:
        anime = watcher.get(int(inp)-1)
    except IndexError:
        sys.exit(0)

    # Make the selected anime first result
    watcher.update(anime)

    while True:
        click.clear()
        click.secho('Title: ' + click.style(anime.title,
                                            fg='green', bold=True))
        click.echo('episodes_done: {}'.format(click.style(
            str(anime.episodes_done), bold=True, fg='yellow')))
        click.echo('Length: {}'.format(len(anime)))
        click.echo('Provider: {}'.format(anime.sitename))

        meta = ''
        for k, v in anime.meta.items():
            meta += '{}: {}\n'.format(k, click.style(v, bold=True))
        click.echo(meta)

        click.echo('Available Commands: set, remove, update, watch,'
                   ' download.\n')

        inp = click.prompt('Press q to exit', default='q').strip()

        # TODO: A better way to handle commands. Use regex. Refractor to class?
        # Decorator?
        if inp == 'q':
            break
        elif inp == 'remove':
            watcher.remove(anime)
            break
        elif inp == 'update':
            watcher.update_anime(anime)
        elif inp == 'watch':
            anime.quality = quality
            watch_anime(watcher, anime)
            sys.exit(0)
        elif inp.startswith('download'):
            try:
                inp = inp.split('download ')[1]
            except IndexError:
                inp = ':'
            inp = str(anime.episodes_done+1) + \
                inp if inp.startswith(':') else inp
            inp = inp+str(len(anime)) if inp.endswith(':') else inp

            anime = util.split_anime(anime, inp)

            if not download_dir:
                download_dir = Config['dl']['download_dir']

            for episode in anime:
                episode.download(force=False,
                                 path=Config['dl']['download_dir'],
                                 format=Config['dl']['file_format'])
        elif inp.startswith('set '):
            inp = inp.split('set ')[-1]
            key, val = [v.strip() for v in inp.split('=')]
            key = key.lower()

            if key == 'title':
                watcher.remove(anime)
                setattr(anime, key, val)
                watcher.add(anime)
            elif key == 'episodes_done':
                setattr(anime, key, int(val))
                watcher.update(anime)
            elif key == 'provider':
                url = util.search(anime.title, val)
                watcher.remove(anime)
                newanime = watcher.new(url)
                newanime.episodes_done = anime.episodes_done
                newanime._timestamp = anime._timestamp
                watcher.update(newanime)
                anime = newanime


def watch_anime(watcher, anime):
    to_watch = anime[anime.episodes_done:]
    logging.debug('Sliced epiosdes: {}'.format(to_watch._episode_urls))

    while anime.episodes_done < len(anime):
        episode = anime[anime.episodes_done]
        anime.episodes_done += 1
        watcher.update(anime)
        for tries in range(5):
            logging.info(
                'Playing episode {}'.format(episode.ep_no)
            )
            try:
                player = mpv(episode.source().stream_url)
            except Exception as e:
                anime.episodes_done -= 1
                watcher.update(anime)
                logging.error(str(e))
                sys.exit(1)

            returncode = player.play()

            if returncode == player.STOP:
                sys.exit(0)
            elif returncode == player.CONNECT_ERR:
                logging.warning("Couldn't connect. Retrying. "
                                "Attempt #{}".format(tries+1))
                continue
            elif returncode == player.PREV:
                anime.episodes_done -= 2
                watcher.update(anime)
                break
            else:
                break
