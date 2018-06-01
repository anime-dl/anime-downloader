import logging
import sys
import shutil
import click
from anime_downloader.sites.nineanime import NineAnime


def setup_logger(log_level):
    if log_level == 'DEBUG':
        format = '%(levelname)s %(name)s: %(message)s'
    else:
        format = '%(levelname)s:%(message)s'

    logging.basicConfig(
        level=logging.getLevelName(log_level),
        format=format
    )


def format_search_results(search_results):
    _, height = shutil.get_terminal_size()
    height -= 4  # Accounting for prompt

    ret = ''
    for idx, result in enumerate(search_results[:height]):
        ret += '{}: {}\n'.format(idx+1, result.title)

    return ret


def search(query):
    # Since this function outputs to stdout this should ideally be in
    # cli. But it is used in watch too. :(
    search_results = NineAnime.search(query)
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
