import logging
import sys
import shutil
import click
import subprocess
import platform


from anime_downloader.sites.nineanime import NineAnime


def setup_logger(log_level):
    if log_level == 'DEBUG':
        format = '%(levelname)s %(name)s: %(message)s'
    else:
        format = click.style('anime', fg='green') + ': %(message)s'

    logging.basicConfig(
        level=logging.getLevelName(log_level),
        format=format
    )

    logger = logging.getLogger('urllib3.connectionpool')
    logger.setLevel(logging.WARNING)


def format_search_results(search_results):
    _, height = shutil.get_terminal_size()
    height -= 4  # Accounting for prompt

    ret = ''
    for idx, result in enumerate(search_results[:height]):
        meta = ''
        meta = ' | '.join(val for _, val in result.meta.items())
        ret += '{:2}: {:40.40}\t{:20.20}\n'.format(idx+1, result.title, meta)

    return ret


def search(query):
    # Since this function outputs to stdout this should ideally be in
    # cli. But it is used in watch too. :(
    try:
        search_results = NineAnime.search(query)
    except Exception as e:
        logging.error(click.style(str(e), fg='red'))
        sys.exit(1)
    click.echo(format_search_results(search_results))

    val = click.prompt('Enter the anime no: ', type=int, default=1)

    try:
        url = search_results[val-1].url
        title = search_results[val-1].title
    except IndexError:
        logging.error('Only maximum of 30 search results are allowed.'
                      ' Please input a number less than 31')
        sys.exit(1)

    logging.info('Selected {}'.format(title))

    return url


def search_and_get_url(query):
    # HACK/XXX: Should use a regex. But a dirty hack for now :/
    if '9anime' not in query:
            return search(query)
    else:
        return query


def split_anime(anime, episode_range):
    try:
        start, end = [int(x) for x in episode_range.split(':')]
        anime._episodeIds = anime._episodeIds[start-1:end-1]
    except ValueError:
        # Only one episode specified
        anime = [anime[int(episode_range)-1]]

    return anime


def print_episodeurl(episode):
    print(episode.stream_url)


def download_episode(episode, **kwargs):
    episode.download(**kwargs)
    print()


def play_episode(episode, *, player):
    p = subprocess.Popen([player, episode.stream_url])
    p.wait()


def print_info(version):
    logging.info('anime-downloader {}'.format(version))
    logging.debug('Platform: {}'.format(platform.platform()))
    logging.debug('Python {}'.format(platform.python_version()))
