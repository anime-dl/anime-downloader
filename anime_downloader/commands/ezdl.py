import logging
import os

import click
import requests_cache

from anime_downloader import session, util
from anime_downloader.__version__ import __version__
from anime_downloader.sites import get_anime_class, ALL_ANIME_SITES
from anime_downloader import animeinfo
from anime_downloader.config import Config

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
    '--play', 'player', metavar='PLAYER',
    help="Streams in the specified player")
@click.option(
    '--force-download', '-f', is_flag=True,
    help='Force downloads even if file exists')
@click.option(
    '--provider',
    help='The anime provider (website) for search.',
    type=click.Choice(sitenames)
)
@click.option(
    '--ratio', '-r',type=int,
    help='Ratio used for the auto select in search. 100 means it only auto selects on complete matches. 0 auto selects regardless of how similar the result is.',
    default=50
)
@click.option(
    '--url', '-u', type=bool, is_flag=True,
    help="If flag is set, prints the stream url instead of downloading")
@click.option("--skip-fillers", is_flag=True, help="Skip downloading of fillers.")

@click.pass_context
def command(ctx, anime_url, episode_range, player,
            force_download, provider,
            skip_fillers, ratio, url):

    # Borrows some config from the original dl command.
    # This can all be flags, but ezdl is made to be easy.
    fallback_qualities = Config['dl']['fallback_qualities']
    download_dir = Config['dl']['download_dir']
    quality = Config['dl']['quality']
    url = Config['dl']['url'] if not url else url
    external_downloader = Config['dl']['external_downloader']
    skip_download = Config['dl']['skip_download']
    chunk_size = Config['dl']['chunk_size']
    speed_limit = Config['dl']['speed_limit']

    fallback_providers = Config['ezdl']['fallback_providers']
    file_format = Config['ezdl']['file_format']

    query = anime_url[:]
    util.print_info(__version__)

    fallback_providers.insert(0, provider)
    # Eliminates duplicates while keeping order
    providers = sorted(set(fallback_providers),key=fallback_providers.index)  

    info = animeinfo.search_anilist(query)
    episode_count = info.episodes - 1
    # Interprets the episode range for use in a for loop.
    # 1:3 -> for _episode in range(1, 4):
    episode_range = util.parse_episode_range(episode_count, episode_range)
    episode_range_split = episode_range.split(':')

    # Stores the choices for each provider, to prevent re-prompting search.
    # As the current setup runs episode wise without this a 12 episode series would give 12+ prompts.
    choice_dict = {}

    # Doesn't work on nyaa since it only returns one episode.
    for episode_range in range(int(episode_range_split[0]), int(episode_range_split[-1])+1):
        # Exits if all providers are skipped.
        if [choice_dict[i] for i in choice_dict] == [0]*len(providers):
            logger.info('All providers skipped, exiting')
            exit()

        for provider in providers:
            if not get_anime_class(provider):
                logger.info('"{}" is an invalid provider'.format(provider))
                continue

            logger.debug('Current provider: {}'.format(provider))
            # TODO: Replace by factory
            cls = get_anime_class(anime_url)

            # To make the downloads use the correct name if URL:s are used.
            real_provider = cls.sitename if cls else provider
            # This will allow for animeinfo metadata in filename and one filename for multiple providers.
            rep_dict = {
                'animeinfo_anime_title': util.slugify(info.title),
                'provider': util.slugify(real_provider),
                'anime_title':'{anime_title}',
                'ep_no':'{ep_no}'
            }
            fixed_file_format = file_format.format(**rep_dict)

            # Keeping this as I don't know the impact of removing it.
            # It's False by default in normal dl.
            disable_ssl = False
            session.get_session().verify = not disable_ssl

            # This is just to make choices in providers presistent between searches.
            choice_provider = choice_dict.get(provider)

            if not cls:
                _anime_url, choice_provider = util.search(anime_url, provider, val=choice_provider, season_info=info, ratio=ratio)
                choice_dict[provider] = choice_provider
                if choice_provider == 0 or not _anime_url:
                    continue

                cls = get_anime_class(_anime_url)

            try:
                anime = cls(_anime_url, quality=quality,
                            fallback_qualities=fallback_qualities)
            # I have yet to investigate all errors this can output
            # No sources found gives error which exits the script
            except:
                continue

            logger.debug('Found anime: {}'.format(anime.title))

            try:
                animes = util.parse_ep_str(anime, str(episode_range))
            except RuntimeError:
                logger.error('No episode found with index {}'.format(episode_range))
                continue
            except:
                logger.error('Unknown provider error')
                continue

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
            for episode in animes:
                if skip_fillers and fillers:
                    if episode.ep_no in fillers:
                        logger.info("Skipping episode {} because it is a filler.".format(episode.ep_no))
                        continue
                
                if url:
                    util.print_episodeurl(episode)

                if player:
                    util.play_episode(episode, player=player, title=f'{anime.title} - Episode {episode.ep_no}')

                if not skip_download:
                    if external_downloader:
                        logging.info('Downloading episode {} of {}'.format(
                            episode.ep_no, anime.title)
                        )
                        util.external_download(external_downloader, episode,
                                               fixed_file_format, path=download_dir, speed_limit=speed_limit)
                        continue
                    if chunk_size is not None:
                        chunk_size = int(chunk_size)
                        chunk_size *= 1e6
                    with requests_cache.disabled():
                        episode.download(force=force_download,
                                         path=download_dir,
                                         format=fixed_file_format,
                                         range_size=chunk_size)
                    print()

            # If it's all successfull proceeds to next ep instead of looping.
            break
