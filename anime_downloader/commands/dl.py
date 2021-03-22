import logging
import os

import click
import requests_cache
import requests

from anime_downloader import session, util
from anime_downloader.__version__ import __version__
from anime_downloader.sites import get_anime_class, ALL_ANIME_SITES, exceptions

logger = logging.getLogger(__name__)

echo = click.echo
sitenames = [v[1] for v in ALL_ANIME_SITES]


# NOTE: Don't put defaults here. Add them to the dict in config
@click.command()
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
    '--choice', '-c', type=int,
    help='Choice to start downloading given anime number '
)
@click.option("--skip-fillers", is_flag=True, help="Skip downloading of fillers.")
@click.option(
    "--speed-limit",
    type=str,
    help="Set the speed limit (in KB/s or MB/s) for downloading when using aria2c",
    metavar='<int>K/M'
)
@click.option("--video-info", "-i", is_flag=True, help="enables getting video information")
@click.pass_context
def command(ctx, anime_url, episode_range, url, player, skip_download, quality,
            force_download, download_dir, file_format, provider,
            external_downloader, chunk_size, disable_ssl, fallback_qualities, choice, skip_fillers, speed_limit, video_info):
    """ Download the anime using the url or search for it.
    """
    query = anime_url[:]

    util.print_info(__version__)
    # TODO: Replace by factory
    cls = get_anime_class(anime_url)

    disable_ssl = cls and cls.__name__ == 'Masterani' or disable_ssl
    session.get_session().verify = not disable_ssl

    if not cls:
        anime_url, _ = util.search(anime_url, provider, choice)
        cls = get_anime_class(anime_url)

    anime = cls(anime_url, quality=quality,
                fallback_qualities=fallback_qualities)
    logger.info('Found anime: {}'.format(anime.title))

    animes = util.parse_ep_str(anime, episode_range)
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
        logger.info('Downloading to {}'.format(os.path.abspath(download_dir)))
    if skip_fillers:
        fillers = util.get_filler_episodes(query)
    if speed_limit:
        logger.info("Speed is being limited to {}".format(speed_limit))
    for episode in animes:
        if video_info:
            import cv2
            cv2video = cv2.VideoCapture(episode.source().stream_url)
            try:
                if cv2video.isOpened():
                    try:
                        framecount = cv2video.get(cv2.CAP_PROP_FRAME_COUNT ) 
                        frames_per_sec = cv2video.get(cv2.CAP_PROP_FPS)
                        duration = framecount / frames_per_sec
                        logger.info(f"Video duration (sec): {duration}")
                    except:
                        logger.warning("Error in video time calculation")
                    try:
                        video_height = cv2video.get(cv2.CAP_PROP_FRAME_HEIGHT)
                        video_width = cv2video.get(cv2.CAP_PROP_FRAME_WIDTH)
                    except:
                        logger.warning("Error in getting video dimensions")
                    try:
                        video_bitrate = cv2video.get(cv2.CAP_PROP_BITRATE)
                    except:
                        logger.warning("Error in getting the bitrate")
                    logger.info(f"Video Dimensions: {video_width} x {video_height}")
                    logger.info(f"Video Bitrate in kbps: {video_bitrate}")
                elif not cv2video.isOpened():
                    logger.warning("File cannot be opened")
            except:
                logger.warning("something went horribly wrong")

        if skip_fillers and fillers:
            if episode.ep_no in fillers:
                logger.info(
                    "Skipping episode {} because it is a filler.".format(episode.ep_no))
                continue

        if url:
            util.print_episodeurl(episode)

        if player:
            episode_range = f"0:{len(animes)}" if not episode_range else episode_range
            util.play_episode(
                episode, player=player, title=f'{anime.title} - Episode {episode.ep_no}', episodes=episode_range)

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
