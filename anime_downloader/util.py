import logging
import sys
import shutil
import click
import subprocess
import platform
import re
import os
import json
import errno
import time
import ast
import math
import coloredlogs
import pickle
import tempfile
import requests
from tabulate import tabulate
from uuid import uuid4
from secrets import choice
from urllib.parse import urlparse, unquote

from anime_downloader import session
from anime_downloader.sites import get_anime_class, helpers
from anime_downloader.const import desktop_headers, get_random_header

logger = logging.getLogger(__name__)

__all__ = [
    'check_in_path',
    'setup_logger',
    'format_search_results',
    'search',
    'split_anime',
    'parse_episode_range',
    'parse_ep_str',
    'print_episodeurl',
    'play_episode',
    'print_info',
]


def check_in_path(app):
    """
    Checks to see if the given app exists on the path
    :param app: app name to look for
    :return: true if the app exists, false otherwise
    """
    return shutil.which(app) is not None


def setup_logger(log_level):
    if log_level == 'DEBUG':
        format = '%(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s'
        from http.client import HTTPConnection
        HTTPConnection.debuglevel = 1
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    else:
        format = click.style('anime', fg='green') + ': %(message)s'

    logger = logging.getLogger("anime_downloader")
    coloredlogs.install(level=log_level, fmt=format, logger=logger)


def format_search_results(search_results):
    headers = [
        'SlNo',
        'Title',
        'Meta',
    ]
    table = [(i + 1, v.title, v.pretty_metadata)
             for i, v in enumerate(search_results)]
    table = tabulate(table, headers, tablefmt='psql')
    table = '\n'.join(table.split('\n')[::-1])
    return table


def search(query, provider, val=None, season_info=None, ratio=50):
    # Will use animeinfo sync if season_info is provided

    # Since this function outputs to stdout this should ideally be in
    # cli. But it is used in watch too. :(
    cls = get_anime_class(provider)
    search_results = cls.search(query)

    if not search_results:
        logger.error('No such Anime found. Please ensure correct spelling.')
        return None, None

    if season_info:
        from anime_downloader import animeinfo
        match = animeinfo.fuzzy_match_metadata([season_info], search_results)
        logger.debug('Match ratio: {}'.format(match.ratio))
        # ratios are a range between 0-100 where 100 means 100% match.
        if match.ratio >= ratio and not val:
            logger.debug('Selected {}'.format(match.SearchResult.title))
            return match.SearchResult.url, None

    click.echo(format_search_results(search_results), err=True)
    # Loop to allow re-propmt if the user chooses incorrectly
    # Makes it harder to unintentionally exit the anime command if it's automated
    while True:
        if val == None:
            val = click.prompt('Enter the anime no{}:'. format(' (0 to switch provider)' * (season_info != None)),
                               type=int, default=1, err=True)
        try:
            url = search_results[val - 1].url
            title = search_results[val - 1].title
        except IndexError:
            logger.error('Only maximum of {} search results are allowed.'
                         ' Please input a number less than {}'.format(
                             len(search_results), len(search_results) + 1))
            val = False
            continue
        break

    # Doesn't print if skipped.
    if season_info is None or val != 0:
        logger.info('Selected {}'.format(title))

    return url, val


def primitive_search(search_results):
    headers = [
        'SlNo',
        'Title',
    ]
    table = [(i + 1, v.title)
             for i, v in enumerate(search_results)]
    table = tabulate(table, headers, tablefmt='psql')
    table = '\n'.join(table.split('\n')[::-1])
    click.echo(table, err=True)

    while True:
        val = click.prompt('Enter the anime no: ',
                           type=int, default=1, err=True)
        try:
            return search_results[val - 1]
        except IndexError:
            logger.error('Only maximum of {} search results are allowed.'
                         ' Please input a number less than {}'.format(
                             len(search_results), len(search_results) + 1))


def download_metadata(file_format, metdata, episode, filename='metdata.json'):
    # turns '{animeinfo_anime_title}/{animeinfo_anime_title}_{provider}_{ep_no}'
    # to '{animeinfo_anime_title}/'
    location = ''.join(file_format.split('/')[:-1])
    location = format_filename(location, episode)
    location_metadata = location + '/' + filename
    if os.path.isfile(location_metadata):
        logger.debug('Metadata file already downloaded.')
        return False

    make_dir(location)

    with open(location_metadata, 'w') as file:
        json.dump(metdata, file, indent=4)
    logger.debug('Downloaded metadata to "{}".'.format(location_metadata))
    return location_metadata


def split_anime(anime, episode_range):
    from anime_downloader.sites.anime import AnimeEpisode
    try:
        start, end = [int(x) for x in episode_range.split(':')]
        ep_range = [x for x in range(start, end)]
        eps = [x for x in anime._episode_urls if x[0] in ep_range]

        anime._episode_urls = [(x[0], x[1]) for x in eps]
        anime._len = len(anime._episode_urls)
    except ValueError:
        # Only one episode specified
        episode = int(episode_range)
        anime = anime[episode - 1:episode]

    return anime


def parse_episode_range(max_range, episode_range):
    if not episode_range:
        episode_range = '1:'
    if episode_range.endswith(':'):
        length = max_range if type(max_range) == int else (
            int(max_range._episode_urls[-1][0]))
        episode_range += str(length + 1)
    if episode_range.startswith(':'):
        episode_range = '1' + episode_range
    return episode_range


def parse_ep_str(anime, grammar):
    episodes = []
    if not grammar:
        return split_anime(anime, parse_episode_range(anime, grammar))

    for episode_grammar in grammar.split(','):
        if ':' in episode_grammar:
            start, end = parse_episode_range(anime, episode_grammar).split(':')
            episode_grammar = '%d:%d' % (int(start), int(end) + 1)
            for episode in split_anime(anime, episode_grammar):
                episodes.append(episode)
        else:
            from anime_downloader.sites.anime import AnimeEpisode

            if grammar == '0':
                ep = sorted(anime._episode_urls)[-1]
            else:
                ep = [x for x in anime._episode_urls if x[0]
                      == int(grammar)][0]

            ep_cls = AnimeEpisode.subclasses[anime.sitename]

            episodes.append(ep_cls(ep[1], parent=anime, ep_no=ep[0]))
    return episodes


def print_episodeurl(episode):
    # if episode.source().referer != '':
    #    print(episode.source().stream_url + "?referer=" +  episode.source().referer)
    # else:
    # Currently I don't know of a way to specify referer in url itself so leaving it here.
    url = episode.url if episode.url.startswith(
        "magnet") else episode.source().stream_url
    print(unquote(url))


def play_episode(episode, *, player, title, episodes="0:0"):
    if player == 'mpv':
        p = subprocess.Popen([player,
                              f'--title={title}',
                              f'--referrer={episode.source().referer}',
                              f'--user-agent={get_random_header()["user-agent"]}',
                              episode.source().stream_url])
    elif player == "android":
        p = subprocess.Popen(['am', 'start', '-a', 'android.intent.action.VIEW',
                              '-t', 'video/*', '-d', f'{episode.source().stream_url}'])
        if episodes == None or ':' in episodes and episodes != "0:1":
            input("Press enter to continue\n")
    else:
        p = subprocess.Popen([player, episode.source().stream_url])
    p.wait()


def print_info(version):
    logger.info('anime-downloader {}'.format(version))
    logger.debug('Platform: {}'.format(platform.platform()))
    logger.debug('Python {}'.format(platform.python_version()))


def get_json(url, params=None):
    logger.debug('API call URL: {} with params {!r}'.format(url, params))
    res = session.get_session().get(url, headers=desktop_headers, params=params)
    logger.debug('URL: {}'.format(res.url))
    data = res.json()
    logger.debug('Returned data: {}'.format(data))

    return data


def slugify(file_name):
    file_name = str(file_name).strip().replace(' ', '_')
    # First group removes filenames starting with a dot making them hidden.
    # Second group removes anything not in it, for example '"/\|
    return re.sub(r'(^\.)|([^-\w.!+-])', '', file_name)


def format_filename(filename, episode):
    zerosTofill = math.ceil(math.log10(episode._parent._len))
    rep_dict = {
        'anime_title': slugify(episode._parent.title),
        'ep_no': str(episode.ep_no).zfill(zerosTofill),
    }

    filename = filename.format(**rep_dict)

    return filename


def format_command(cmd, episode, file_format, speed_limit, path):
    from anime_downloader.config import Config
    if not Config._CONFIG['dl']['aria2c_for_torrents'] and (episode.url.startswith('magnet:?xt=urn:btih:') or episode.source().stream_url.startswith('https://magnet:?xt=urn:btih:')):
        url = episode.url if episode.url.startswith(
            "magnet") else episode.source().stream_url
        url = url.replace("https://", "")
        return ['open', url]

    # For aria2c.
    log_levels = ['debug', 'info', 'notice', 'warn', 'error']
    log_level = Config['dl']['aria2c_log_level'].lower()
    if log_level not in log_levels:
        logger.warn(
            'Invalid logging level "{}", defaulting to "error".'.format(log_level))
        logger.debug('Possible levels: {}.'.format(log_levels))
        log_level = 'error'

    cmd_dict = {
        '{aria2}': 'aria2c {stream_url} -x 12 -s 12 -j 12 -k 10M -o '
                   '{file_format}.mp4 --continue=true --dir={download_dir} '
                   '--stream-piece-selector=inorder --min-split-size=5M --referer={referer} '
                   '--check-certificate=false --user-agent={useragent} --max-overall-download-limit={speed_limit} '
                   '--console-log-level={log_level}',
        '{idm}': 'idman.exe /n /d {stream_url} /p {download_dir} /f {file_format}.mp4',
        '{wget}': 'wget {stream_url} --referer={referer} --user-agent={useragent} -O {download_dir}/{file_format}.mp4 -c'
    }

    # Allows for passing the user agent with self.headers in the site.
    # Some sites block downloads using a different user agent.
    if episode.headers.get('user-agent'):
        useragent = episode.headers['user-agent']
    else:
        useragent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36'

    stream_url = episode.source().stream_url if not episode.url.startswith(
        'magnet:?xt=urn:btih:') else episode.url
    stream_url = stream_url if 'magnet:?xt=urn:btih:' not in stream_url else stream_url.replace(
        'https://', '')

    rep_dict = {
        'stream_url': stream_url,
        'file_format': file_format,
        'download_dir': os.path.abspath(path),
        'referer': episode.source().referer,
        'useragent': useragent,
        'speed_limit': speed_limit,
        'log_level': log_level
    }

    if cmd == "{wget}":
        # Create the directory if it doesn't exist
        make_dir(
            f"{rep_dict['download_dir']}/{os.path.dirname(format_filename(rep_dict['file_format'], episode))}")
        path_string = file_format.replace('\\', '/').split('/')
        rep_dict['file_format'] = path_string.pop(-1)
        path_string = '/'.join(path_string)
        rep_dict['download_dir'] = os.path.join(path, path_string)

    if cmd == "{idm}":
        rep_dict['file_format'] = rep_dict['file_format'].replace('/', '\\')

    if cmd in cmd_dict:
        cmd = cmd_dict[cmd]

    cmd = cmd.split(' ')
    cmd = [c.format(**rep_dict) for c in cmd]
    cmd = [format_filename(c, episode) for c in cmd]

    return cmd


def deobfuscate_packed_js(packedjs):
    return eval_in_node('eval=console.log; ' + packedjs)


def eval_in_node(js: str):
    # TODO: This should be in util
    output = subprocess.check_output(['node', '-e', js])
    return output.decode('utf-8')


def open_magnet(magnet):
    if sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
        os.startfile(magnet)
    elif sys.platform.startswith('darwin'):
        subprocess.Popen(['open', magnet],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        subprocess.Popen(['xdg-open', magnet],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def external_download(cmd, episode, file_format, speed_limit, path=''):
    logger.debug('cmd: ' + cmd)
    logger.debug('episode: {!r}'.format(episode))
    logger.debug('file format: ' + file_format)

    cmd = format_command(cmd, episode, file_format, speed_limit, path=path)

    logger.debug('formatted cmd: ' + ' '.join(cmd))

    if cmd[0] == 'open':  # for torrents
        open_magnet(cmd[1])
    else:
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


def get_filler_episodes(query):
    def search_filler_episodes(query, page):
        url = 'https://animefillerlist.com/search/node/'
        search_results = helpers.soupify(helpers.get(
            url + query, params={'page': page})).select('h3.title > a')
        urls = [a.get('href') for a in search_results if a.get(
            'href').split('/')[-2] == 'shows']
        search_results = [
            [
                search_results[a].text]
            for a in range(len(search_results)) if search_results[a].get('href').split('/')[-2] == 'shows'
        ]
        return search_results, urls

    results_list, urls_list = [], []
    prev = ['']

    for a in range(5):  # Max 5 pages, could be done using the pager element
        search_results, urls = search_filler_episodes(query, a)
        # stops the loop if the same site is visited twice
        if urls == prev and not (len(urls) == 0 or a == 0):
            break
        prev = urls[:]

        for b in search_results:
            results_list.append(b)
        for c in urls:
            urls_list.append(c)

    [results_list[a].insert(0, a + 1)
     for a in range(len(results_list))]  # inserts numbers

    headers = ["SlNo", "Title"]
    table = tabulate(results_list, headers, tablefmt='psql')
    table = '\n'.join(table.split('\n')[::-1])

    click.echo(table)
    val = click.prompt(
        'Enter the filler-anime no (0 to cancel): ', type=int, default=1, err=True)
    if val == 0:
        return False

    url = urls_list[val - 1]

    try:
        logger.info("Fetching filler episodes...")

        res = helpers.get(url)
        soup = helpers.soupify(res.text)

        episodes = []

        for filler_episode in soup.find("div", attrs={"class": "filler"}).find_all("a"):
            txt = filler_episode.text.strip()
            if '-' in txt:
                split = txt.split('-')
                for a in range(int(split[0]), int(split[1]) + 1):
                    episodes.append(a)
            else:
                episodes.append(int(txt))

        logger.debug("Found {} filler episodes.".format(len(episodes)))
        return episodes

    except:
        logger.warn(
            "Can't get filler episodes. Will download all specified episodes.")
        return False


class ClickListOption(click.Option):

    def type_cast_value(self, ctx, value):
        try:
            if isinstance(value, list):
                return value
            return ast.literal_eval(value)
        except:
            raise click.BadParameter(value)
