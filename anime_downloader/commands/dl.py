import logging
import os
import re

import click
import requests_cache

from anime_downloader import session, util
from anime_downloader.__version__ import __version__
from anime_downloader.sites import get_anime_class, ALL_ANIME_SITES, exceptions
from click.exceptions import UsageError

logger = logging.getLogger(__name__)

echo = click.echo
sitenames = [v[1] for v in ALL_ANIME_SITES]


# NOTE: Don't put defaults here. Add them to the dict in config
@click.command()
@click.argument('anime_url')
@click.option(
    '--episodes', '-e', 'episode_range', metavar='<int>:<int>',
    help="Range of anime you want to download in the form <start>:<end>. If used with the -q/--queue flag, this must be a comma delimited list, e.g: <start>:<end>,<start>:<end> - the length must match the length of the number of anime provided")
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
    help="Specify the directory to download to")
@click.option(
    '--quality', '-q', type=click.Choice(['360p', '480p', '720p', '1080p']),
    help='Specify the quality of episode. Default-720p')
@click.option(
    '--fallback-qualities', '-fq', cls=util.ClickListOption,
    help='Specify the order of fallback qualities as a list.')
@click.option(
    '--force-download', '-f', is_flag=True,
    help='Force downloads even if file exists')
@click.option(
    '--file-format', '-ff', default='{anime_title}/{anime_title}_{ep_no}',
    help='Format for how the files to be downloaded be named.',
    metavar='FORMAT STRING'
)
@click.option(
    '-p', '--provider',
    help='The anime provider (website) for search.',
    type=click.Choice(sitenames)
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
@click.option(
    '--disable-ssl',
    is_flag=True,
    help='Disable verifying the SSL certificate, if flag is set'
)
@click.option(
    '--choice', '-c', type=str,
    help='Choice to start downloading given anime number. If used with the -q/--queue flag, this must be a comma delimited list, e.g: -c number,number - the length must match the length of the number of anime provided'
)
@click.option("--skip-fillers", is_flag=True, help="Skip downloading of fillers.")
@click.option(
    "--speed-limit",
    type=str,
    help="Set the speed limit (in KB/s or MB/s) for downloading when using aria2c",
    metavar='<int>K/M'
)
@click.option(
    "--queue", "-q",
    type=bool, is_flag=True,
    help="Queue a series of anime"
)
@click.pass_context
def command(ctx, anime_url, episode_range, url, player, skip_download, quality,
            force_download, download_dir, file_format, provider,
            external_downloader, chunk_size, disable_ssl, fallback_qualities, choice, skip_fillers, speed_limit, queue):
    """ Download the anime using the url or search for it.
    """
    # Broken down by comma, and re-joined with comma, to remove trailing commas for accuracy with following len checks against choice and episode_range
    anime_url = ",".join([x.strip() for x in anime_url.split(",") if x.strip() != ''])
    if choice:
        # Ensure that choice is only a combination of commas and numbers
        match = re.match("[\d,]+", choice)
        if not match or match.group() != choice:
            raise UsageError(f"Invalid value for '--choice' / '-c': {choice} is not a valid integer/list of comma-delimited list of integers")

        choice = [x.strip() for x in choice.split(",") if x.strip()]
        # Check that length matches of choice list is equivalent to the number of specified anime
        if len(choice) != len(anime_url.split(",")):
            raise UsageError(f"Invalid value for '--choice' / '-c': {','.join(choice)} does not have an equivalent number of arguments to {anime_url}")


    if episode_range:
        # Check that only numeric characters, ',', and ':' are used
        match = re.match("[\d:,]+", episode_range)

        if not match or match.group() != episode_range:
            raise UsageError("Invalid value for '--episodes' / '-e': only numerical characters, ',', and ':' are allowed")

        episode_range = [x.strip() for x in episode_range.split(",") if x.strip()]

        if len(episode_range) != len(anime_url.split(",")):
            raise UsageError(f"Invalid value for '--episodes' / '-e: {','.join(episode_range)} does not have an equivalent number of arguments to {anime_url}")

    # anime_url changes after the first anime in the queue to the link of the previous anime
    original_url = anime_url
    for i in range(len(original_url.split(","))):
        query = original_url.split(",")[i][:]
        logger.info(original_url.split(","))

        util.print_info(__version__)
        # TODO: Replace by factory
        cls = get_anime_class(original_url.split(",")[i])

        disable_ssl = cls and cls.__name__ == 'Masterani' or disable_ssl
        session.get_session().verify = not disable_ssl

        if not cls:
            # Current choice is used, so if the user doesn't use the -c flag, there isn't a "NoneType isn't subscriptable error" when trying to index choice
            current_choice = None
            if choice:
                current_choice = int(choice[i])

            anime_url, _ = util.search(original_url.split(",")[i], provider, current_choice)
            cls = get_anime_class(anime_url)

        anime = cls(anime_url, quality=quality,
                    fallback_qualities=fallback_qualities)
        logger.info('Found anime: {}'.format(anime.title))

        current_range = None
        if episode_range:
            current_range = episode_range[i]
        animes = util.parse_ep_str(anime, current_range)
        if not animes:
            # Issue #508.
            raise exceptions.NotFoundError('No episodes found within index.')

        # TODO:
        # Two types of plugins:
        #   - Aime plugin: Pass the whole anime
        #   - Ep plugin: Pass each episode
        if url or player:
            skip_download = True

        if download_dir and not skip_download:
            logger.info('Downloading to {}'.format(
                os.path.abspath(download_dir)))
        if skip_fillers:
            fillers = util.get_filler_episodes(query)
        if speed_limit:
            logger.info("Speed is being limited to {}".format(speed_limit))
        for episode in animes:
            if skip_fillers and fillers:
                if episode.ep_no in fillers:
                    logger.info(
                        "Skipping episode {} because it is a filler.".format(episode.ep_no))
                    continue

            if url:
                util.print_episodeurl(episode)

            if player:
                util.play_episode(episode, player=player,
                                  title=f'{anime.title} - Episode {episode.ep_no}')

            if not skip_download:
                if external_downloader:
                    logging.info('Downloading episode {} of {}'.format(
                        episode.ep_no, anime.title)
                    )
                    util.external_download(external_downloader, episode,
                                           file_format, speed_limit, path=download_dir)
                    continue
                if chunk_size is not None:
                    chunk_size *= 1e6
                    chunk_size = int(chunk_size)
                with requests_cache.disabled():
                    episode.download(force=force_download,
                                     path=download_dir,
                                     format=file_format,
                                     range_size=chunk_size)
                print()
