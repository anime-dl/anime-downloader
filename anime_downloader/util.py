import logging
import sys
import shutil
import click
import subprocess
import platform
import requests
import re
import os
import errno
import time
import ast

from anime_downloader.sites import get_anime_class
from anime_downloader.const import desktop_headers


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
        try:
            meta = ' | '.join(val for _, val in result.meta.items())
        except AttributeError:
            meta = ''
        ret += '{:2}: {:40.40}\t{:20.20}\n'.format(idx+1, result.title, meta)

    return ret


def search(query, provider):
    # Since this function outputs to stdout this should ideally be in
    # cli. But it is used in watch too. :(
    cls = get_anime_class(provider)
    try:
        search_results = cls.search(query)
    except Exception as e:
        logging.error(click.style(str(e), fg='red'))
        sys.exit(1)
    click.echo(format_search_results(search_results))

    if not search_results:
        logging.error('No such Anime found. Please ensure correct spelling.')
        sys.exit(1)

    val = click.prompt('Enter the anime no: ', type=int, default=1)

    try:
        url = search_results[val-1].url
        title = search_results[val-1].title
    except IndexError:
        logging.error('Only maximum of {} search results are allowed.'
                      ' Please input a number less than {}'.format(
                          len(search_results), len(search_results)+1))
        sys.exit(1)

    logging.info('Selected {}'.format(title))

    return url


def split_anime(anime, episode_range):
    try:
        start, end = [int(x) for x in episode_range.split(':')]
        anime = anime[start-1:end-1]
    except ValueError:
        # Only one episode specified
        episode = int(episode_range)
        anime = anime[episode-1:episode]

    return anime


def print_episodeurl(episode):
    print(episode.source().stream_url)


def download_episode(episode, **kwargs):
    episode.download(**kwargs)
    print()


def play_episode(episode, *, player):
    p = subprocess.Popen([player, episode.source().stream_url])
    p.wait()


def print_info(version):
    logging.info('anime-downloader {}'.format(version))
    logging.debug('Platform: {}'.format(platform.platform()))
    logging.debug('Python {}'.format(platform.python_version()))


def get_json(url, params=None):
    logging.debug('API call URL: {} with params {!r}'.format(url, params))
    res = requests.get(url, headers=desktop_headers, params=params)
    logging.debug('URL: {}'.format(res.url))
    data = res.json()
    logging.debug('Returned data: {}'.format(data))

    return data


def slugify(file_name):
    file_name = str(file_name).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', file_name)


def format_filename(filename, episode):
    rep_dict = {
        'anime_title': slugify(episode._parent.title),
        'ep_no': episode.ep_no,
    }

    filename = filename.format(**rep_dict)

    return filename


def format_command(cmd, episode, file_format, path):
    cmd_dict = {
        '{aria2}': 'aria2c {stream_url} -x 12 -s 12 -j 12 -k 10M -o '
                   '{file_format}.mp4 --continue=true --dir={download_dir}'
                   ' --stream-piece-selector=inorder --min-split-size=5M'
    }
    rep_dict = {
        'stream_url': episode.source().stream_url,
        'file_format': file_format,
        'download_dir': os.path.abspath(path),
    }

    if cmd in cmd_dict:
        cmd = cmd_dict[cmd]

    cmd = cmd.split(' ')
    cmd = [c.format(**rep_dict) for c in cmd]
    cmd = [format_filename(c, episode) for c in cmd]

    return cmd


def external_download(cmd, episode, file_format, path=''):
    logging.debug('cmd: ' + cmd)
    logging.debug('episode: {!r}'.format(episode))
    logging.debug('file format: ' + file_format)

    cmd = format_command(cmd, episode, file_format, path=path)

    logging.debug('formatted cmd: ' + ' '.join(cmd))

    p = subprocess.Popen(cmd)
    return_code = p.wait()

    if return_code != 0:
        # Sleep for a while to make sure downloader exits correctly
        time.sleep(2)
        sys.exit(1)


def make_dir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


class ClickListOption(click.Option):

    def type_cast_value(self, ctx, value):
        try:
            if isinstance(value, list):
                return value
            return ast.literal_eval(value)
        except:
            raise click.BadParameter(value)
