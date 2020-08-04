import click
import logging
import sys
import re

from anime_downloader import util
from anime_downloader.__version__ import __version__
from anime_downloader.players.mpv import mpv
from anime_downloader import watch as _watch
from anime_downloader.config import Config
from anime_downloader.sites import get_anime_class, ALL_ANIME_SITES
logger = logging.Logger(__name__)

echo = click.echo
sitenames = [v[1] for v in ALL_ANIME_SITES]

@click.command()
@click.argument('anime_name', required=False)
@click.option(
    '--new', '-n', type=bool, is_flag=True,
    help="Create a new anime to watch")
@click.option(
    '--list', '-l', '_list', type=click.Choice(['all','watching','completed','planned','dropped']), help="List all animes in watch list")
@click.option(
    '--remove', '-r', 'remove', type=bool, is_flag=True,
    help="Remove the specified anime")
@click.option(
    '--update-all', '-u', 'update_all', type=bool, is_flag=True, help="Update the episodes of all anime in your list"
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
    type=click.Choice(sitenames)
)

def command(anime_name, new, update_all, _list, quality, remove,
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
    back       : Returns back to the list
    """
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

    # Defaults the command to anime watch -l all.
    # It's a bit of a hack to use sys.argv, but doesn't break
    # if new commands are added (provided you used a bunch of and statements)
    _list = 'all' if sys.argv[-1] == 'watch' else _list
    if _list:
        filt = _list
        list_animes(watcher, quality, download_dir, None, _filter = filt)
        sys.exit(0)

    if anime_name:
        anime = watcher.get(anime_name)
        if not anime:
            logger.error(
                "Couldn't find '{}'."
                "Use a better search term.".format(anime_name))
            sys.exit(1)

        anime.quality = quality

        logger.info('Found {}'.format(anime.title))
        watch_anime(watcher, anime,quality,download_dir)

def command_parser(command):
    # Returns a list of the commands
    # new "no neverland" --provider vidstream > ['new', '--provider', 'no neverland', 'vidstream']

    # Better than split(' ') because it accounts for quoutes.
    # Group 3 for qouted command
    command_regex = r'(("|\')(.*?)("|\')|.*?\s)'
    matches = re.findall(command_regex,command + " ")
    commands = [i[0].strip('"').strip("'").strip() for i in matches if i[0].strip()]
    return commands

def list_animes(watcher, quality, download_dir, imp = None, _filter = None):

    click.echo('Available Commands: swap, new')
    watcher.list(filt= _filter)
    inp = click.prompt('Select an anime', default="1") if not imp else imp
    provider = Config['watch']['provider']
    # Not a number as input and command
    if not str(inp).isnumeric():
        if ' ' in str(inp).strip():
            args = command_parser(str(inp))
            key = args[0].lower()
            vals = args[1:]
            if key == 'new':
                query = vals[0]
                if '--provider' in vals:
                    if vals.index('--provider') + 1 < len(vals):
                        provider = vals[vals.index('--provider') + 1]
                url = util.search(query, provider)
                watcher.new(url)

            if key == 'swap':
                if vals[0] in ['all','watching','completed','planned','dropped']:
                    return list_animes(watcher, quality, download_dir, imp=imp, _filter=vals[0])

            return list_animes(watcher, quality, download_dir, imp=imp)
        else:
            # Exits if neither int or actual command
            sys.exit(0)

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
        click.echo('Score: {}'.format(anime.score))
        click.echo('Watch Status: {}'.format(anime.watch_status))
        meta = ''
        for k, v in anime.meta.items():
            meta += '{}: {}\n'.format(k, click.style(str(v), bold=True))
        click.echo(meta)

        click.echo('Available Commands: set, remove, update, watch, back,'
                   ' download.\n')

        inp = click.prompt('Press q to exit', default='q').strip()

        # TODO: A better way to handle commands. Use regex. Refractor to class?
        # Decorator?
        if inp == 'q':
            sys.exit(0)
        elif inp == 'back':
            list_animes(watcher, quality, download_dir, imp=imp)
        elif inp == 'remove':
            watcher.remove(anime)
            list_animes(watcher, quality, download_dir, imp=imp)
        elif inp == 'update':
            watcher.update_anime(anime)
        elif inp == 'watch':
            anime.quality = quality
            watch_anime(watcher, anime,quality, download_dir)

        elif inp.startswith('download'):
            # You can use download 3:10 for selected episodes
            try:
                inp = inp.split('download ')[1]
            except IndexError:
                inp = ':'
            animes = util.parse_ep_str(anime, inp)

            # Using the config from dl.
            if not download_dir:
                download_dir = Config['dl']['download_dir']
            # These things could be flags.
            external_downloader = Config['dl']['external_downloader']
            file_format = Config['dl']['file_format']
            speed_limit = Config['dl']['speed_limit']

            for episode in animes:
                util.external_download(external_downloader, episode,
                                       file_format, speed_limit, path=download_dir)

        elif inp.startswith('set '):
            inp = inp.split('set ')[-1]
            key, val = [v.strip() for v in inp.split('=')]
            key = key.lower()

            if key == 'title':
                watcher.remove(anime)
                setattr(anime, key, val)
                watcher.add(anime)

            elif key == 'episodes_done':
                # Retries if invalid input.
                if not val.isnumeric():
                    # Uncomment this if you want to let the user know.
                    #logger.error("Invalid integer")
                    #input()
                    continue
                # Prevents setting length above max amount of episodes.
                val = val if int(val) <= len(anime) else len(anime)
                setattr(anime, key, int(val))
                watcher.update(anime)

            elif key == 'provider':
                # Checks if it's an invalid provider preventing errors.
                if not get_anime_class(val):
                    # Probably good to list providers here before looping.
                    continue
                # Watch can quit if no anime is found, not ideal.
                url = util.search(anime.title, val)
                watcher.remove(anime)
                newanime = watcher.new(url)
                newanime.episodes_done = anime.episodes_done
                newanime.score = anime.score
                newanime.watch_status = anime.watch_status
                newanime._timestamp = anime._timestamp
                watcher.update(newanime)
                anime = newanime

            elif key == 'score':
                anime.score = val
                watcher.update(anime)

            elif key == 'watch_status':
                if val in ['watching','completed','dropped','planned','all']:
                    colours = {
                        'watching':'blue',
                        'completed':'green',
                        'dropped':'red',
                        'planned':'yellow',
                    }
                    anime.watch_status = val
                    anime.colours = colours.get(anime.watch_status,'yellow')
                    watcher.update(anime)


def watch_anime(watcher, anime, quality, download_dir):
    autoplay = Config['watch']['autoplay_next']
    to_watch = anime[anime.episodes_done:]
    logger.debug('Sliced episodes: {}'.format(to_watch._episode_urls))

    while anime.episodes_done < len(anime):
        episode = anime[anime.episodes_done]
        anime.episodes_done += 1
        watcher.update(anime)
        for tries in range(5):
            logger.info(
                'Playing episode {}'.format(episode.ep_no)
            )
            try:
                player = mpv(episode)
            except Exception as e:
                anime.episodes_done -= 1
                watcher.update(anime)
                logger.error(str(e))
                sys.exit(1)

            returncode = player.play()
            if returncode == player.STOP:
                # Returns to watch.
                return

            elif returncode == player.CONNECT_ERR:
                logger.warning("Couldn't connect. Retrying. "
                                "Attempt #{}".format(tries+1))
                continue

            elif returncode == player.PREV:
                anime.episodes_done -= 2
                watcher.update(anime)
                break
            # If no other return codes, basically when the player finishes.
            # Can't find the returncode for success.
            elif autoplay:
                break
            else:
                return
