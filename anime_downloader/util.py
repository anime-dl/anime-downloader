import logging
import sys
import shutil
import click
import subprocess
import platform
import re
import os
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
from urllib.parse import urlparse

from anime_downloader import session
from anime_downloader.sites import get_anime_class, helpers
from anime_downloader.const import desktop_headers

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
    'download_episode',
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
    table = [(i+1, v.title, v.pretty_metadata)
             for i, v in enumerate(search_results)]
    table = tabulate(table, headers, tablefmt='psql')
    table = '\n'.join(table.split('\n')[::-1])
    return table


def search(query, provider, choice=None):
    # Since this function outputs to stdout this should ideally be in
    # cli. But it is used in watch too. :(
    cls = get_anime_class(provider)
    search_results = cls.search(query)
    click.echo(format_search_results(search_results), err=True)

    if not search_results:
        logger.error('No such Anime found. Please ensure correct spelling.')
        sys.exit(1)

    if choice:
        val = choice
    else:
        val = click.prompt('Enter the anime no: ', type=int, default=1, err=True)

    try:
        url = search_results[val-1].url
        title = search_results[val-1].title
    except IndexError:
        logger.error('Only maximum of {} search results are allowed.'
                     ' Please input a number less than {}'.format(
                         len(search_results), len(search_results)+1))
        sys.exit(1)


    logger.info('Selected {}'.format(title))

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


def parse_episode_range(anime, episode_range):
    if not episode_range:
        episode_range = '1:'
    if episode_range.endswith(':'):
        episode_range += str(len(anime) + 1)
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
            episodes.append(anime[int(episode_grammar) - 1])
    return episodes


def print_episodeurl(episode):
    # if episode.source().referer != '':
    #    print(episode.source().stream_url + "?referer=" +  episode.source().referer)
    # else:
    # Currently I don't know of a way to specify referer in url itself so leaving it here.
    print(episode.source().stream_url)


def download_episode(episode, **kwargs):
    episode.download(**kwargs)
    print()


def play_episode(episode, *, player, title):
    if player == 'mpv':
        p = subprocess.Popen([
            player,
            '--title={}'.format(title),
            '--referrer="{}"'.format(episode.source().referer),
            episode.source().stream_url
            ])
    else:
        p = subprocess.Popen([ player, episode.source().stream_url
            ])
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
    return re.sub(r'(?u)[^-\w.]', '', file_name)


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
    if not Config._CONFIG['dl']['aria2c_for_torrents'] and episode.url.startswith('magnet:?xt=urn:btih:'):
        return ['open',episode.url]

    cmd_dict = {
        '{aria2}': 'aria2c {stream_url} -x 12 -s 12 -j 12 -k 10M -o '
                   '{file_format}.mp4 --continue=true --dir={download_dir}'
                   ' --stream-piece-selector=inorder --min-split-size=5M --referer={referer} --check-certificate=false --user-agent={useragent} --max-overall-download-limit={speed_limit}',
        '{idm}'  : 'idman.exe /n /d {stream_url} /p {download_dir} /f {file_format}.mp4'
    }


    rep_dict = {
        'stream_url': episode.source().stream_url if not episode.url.startswith('magnet:?xt=urn:btih:') else episode.url,
        'file_format': file_format,
        'download_dir': os.path.abspath(path),
        'referer': episode.source().referer,
        'useragent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',
        'speed_limit': speed_limit
    }

    if cmd == "{idm}":
        rep_dict['file_format'] = rep_dict['file_format'].replace('/','\\')

    if cmd in cmd_dict:
        cmd = cmd_dict[cmd]

    cmd = cmd.split(' ')
    cmd = [c.format(**rep_dict) for c in cmd]
    cmd = [format_filename(c, episode) for c in cmd]
    return cmd


#Credits to: https://github.com/Futei/SineCaptcha
def bypass_hcaptcha(url):
    """
    :param url: url to page which gives hcaptcha
    :return: Returns Response object (cookies stored for future use)
    """
    host = urlparse(url).netloc
    bypassed = False
    session = requests.session()

    headers = {
        'User-Agent': choice((
            'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/605.1.15 (KHTML, like Gecko)',
            'Mozilla/5.0 (iPad; CPU OS 9_3_5 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13G36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
            ))
        }

    logger.info("Bypassing captcha...")

    #Retry until success
    while not bypassed:
        site_key = str(uuid4())
        response = session.post('https://hcaptcha.com/getcaptcha', headers = headers, data = {
            'sitekey': site_key,
            'host': host
            }).json()

        try:
            key = response['key']
            tasks = [row['task_key'] for row in response['tasklist']]
            job = response['request_type']
            timestamp = round(time()) + choice(range(30, 120))
            answers = dict(zip(tasks, [choice(['true', 'false']) for index in range(len(tasks))]))

            mouse_movements = []
            last_movement = timestamp

            for index in range(choice(range(1000, 10000))):
                last_movement += choice(range(10))
                mouse_movements.append([choice(range(500)), choice(range(500)), last_movement])

            json = {
                'job_mode': job,
                'answers': answers,
                'serverdomain': host,
                'sitekey': site_key,
                'motionData': {
                    'st': timestamp,
                    'dct': timestamp,
                    'mm': mouse_movements
                    }
                }

            response = session.post(f'https://hcaptcha.com/checkcaptcha/{key}', json = json)

            response = response.json()
            bypassed = response['pass']
        except (TypeError, KeyError):
            pass

        if bypassed:
            token = response['generated_pass_UUID']

            resp = helpers.soupify(session.get(url))
            bypass_url = f'https://{host}{resp.form.get("action")}'

            data = dict((x.get('name'), x.get('value')) for x in resp.select('form > input'))
            data.update({'id': resp.strong.text, 'g-recaptcha-response': token, 'h-captcha-response': token})

            resp = session.post(bypass_url, data = data)

            if resp.status_code == 200:
                pickle.dump(resp.cookies, open(f'{tempfile.gettempdir()}/{host}', 'wb'))
                logger.info("Succesfully bypassed captcha!")
                
                return resp
            else:
                bypassed = False


def get_hcaptcha_cookies(url):
    """
    :param url: url that you want to use cookies for
    :return: returns cookies if they were stored, or nothing, if they weren't
    """

    COOKIE_FILE = f'{tempfile.gettempdir()}/{urlparse(url).netloc}'

    if os.path.isfile(COOKIE_FILE):
        return pickle.load(open(COOKIE_FILE, 'rb'))

def deobfuscate_packed_js(packedjs):
    return eval_in_node('eval=console.log; ' + packedjs)


def eval_in_node(js: str):
    # TODO: This should be in util
    output = subprocess.check_output(['node', '-e', js])
    return output.decode('utf-8')

def open_magnet(magnet):
    if sys.platform.startswith('linux'):
        subprocess.Popen(['xdg-open', magnet],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif sys.platform.startswith('win32'):
        os.startfile(magnet)
    elif sys.platform.startswith('cygwin'):
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

    if cmd[0] == 'open': #for torrents
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
    def search_filler_episodes(query,page):
        url = 'https://animefillerlist.com/search/node/'
        search_results = helpers.soupify(helpers.get(url+query, params={'page': page})).select('h3.title > a')
        urls = [a.get('href') for a in search_results if a.get('href').split('/')[-2] == 'shows']
        search_results = [
            [
                search_results[a].text]
            for a in range(len(search_results)) if search_results[a].get('href').split('/')[-2] == 'shows'
        ]
        return search_results, urls


    results_list, urls_list = [],[]
    prev = ['']

    for a in range(5): #Max 5 pages, could be done using the pager element
        search_results, urls = search_filler_episodes(query,a)
        if urls == prev and not (len(urls) == 0 or a == 0): #stops the loop if the same site is visited twice
            break
        prev = urls[:]

        for b in search_results:
            results_list.append(b)
        for c in urls:
            urls_list.append(c)
    
    [results_list[a].insert(0,a+1)for a in range(len(results_list))] #inserts numbers
    
    headers = ["SlNo", "Title"]
    table = tabulate(results_list, headers, tablefmt='psql')
    table = '\n'.join(table.split('\n')[::-1])
    
    click.echo(table)
    val = click.prompt('Enter the filler-anime no (0 to cancel): ', type=int, default=1, err=True)
    if val == 0:
        return False

    url = urls_list[val-1]

    try:
        logger.info("Fetching filler episodes...")

        res = helpers.get(url)
        soup = helpers.soupify(res.text)

        episodes = []

        for filler_episode in soup.find("div", attrs={"class": "filler"}).find_all("a"):
            txt = filler_episode.text.strip()
            if '-' in txt:
                split = txt.split('-')
                for a in range(int(split[0]),int(split[1])+1):
                    episodes.append(a)
            else:
                episodes.append(int(txt))
    
        logger.debug("Found {} filler episodes.".format(len(episodes)))
        return episodes
    
    except:
        logger.warn("Can't get filler episodes. Will download all specified episodes.")
        return False


class ClickListOption(click.Option):

    def type_cast_value(self, ctx, value):
        try:
            if isinstance(value, list):
                return value
            return ast.literal_eval(value)
        except:
            raise click.BadParameter(value)
