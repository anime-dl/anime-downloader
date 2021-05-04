import logging
import sys
import threading
import os
import click
from fuzzywuzzy import fuzz

from anime_downloader.sites import get_anime_class, ALL_ANIME_SITES
from anime_downloader import util
from anime_downloader.__version__ import __version__

import requests
logging.getLogger(requests.packages.urllib3.__package__).setLevel(logging.ERROR) #disable Retry warnings

logger = logging.getLogger(__name__)

echo = click.echo
sitenames = [v[1] for v in ALL_ANIME_SITES]


class SiteThread(threading.Thread):
    def __init__(self, provider, anime, verify, v_tries, *args, **kwargs):
        self.provider = provider
        self.anime = anime
        self.verify =  verify
        self.v_tries = v_tries
        self.search_result = None
        self.exception = None
        super().__init__(*args, **kwargs)

    def run(self):
        try:
            ani = get_anime_class(self.provider)
            self.search_result = ani.search(self.anime)
            if self.search_result:
                if self.verify:
                    ratios = [[fuzz.token_set_ratio(self.anime.lower(), sr.title.lower()), sr] for sr in self.search_result]
                    ratios = sorted(ratios, key=lambda x: x[0], reverse=True)
                    
                    end = len(ratios)
                    for r in range(self.v_tries):
                        if r == end: break
                        try:
                            anime_choice = ratios[r][1]
                            anime_url = ani(anime_choice.url)
                            stream_url = anime_url[0].source().stream_url
                            self.exception = None
                            break
                        except Exception as e:
                            self.exception = e
                            
                self.search_result = util.format_search_results(self.search_result)

        except Exception as e:
            self.exception = e

@click.command()
@click.argument('anime', default='naruto')
@click.option(
    '-f', '--prompt-found', is_flag=True,
    help='Ask to stop searching on anime match.')
@click.option(
    '-p', '--providers',
    help='Limit search to specific provider(s) separated by a comma.'
)
@click.option(
    '-e', '--exclude',
    help='Provider(s) to exclude separated by a comma.'
)
@click.option(
    '-v', '--verify', is_flag=True,
    help='Verify extraction of stream url in case of anime match.'
)
@click.option(
    '-n', '--v-tries', type=int, default=1,
    help='Number of tries to extract stream url. (default: 1)'
)
@click.option(
    '-z', '--no-fuzzy', is_flag=True,
    help='Disable fuzzy search to include possible inaccurate results.'
)
@click.option(
    '-r', '--print-results', is_flag=True,
    help='Enable echoing the search results at the end of testing.'
)
@click.option(
    '-t', '--timeout', type=int, default=10,
    help='How long to wait for a site to respond. (default: 10s)'
)

def command(anime, prompt_found, providers, exclude, verify, v_tries, no_fuzzy, print_results, timeout):
    """Test all sites to see which ones are working and which ones aren't. Test naruto as a default. Return results for each provider."""

    util.print_info(__version__)
    logger = logging.getLogger("anime_downloader")
    logger.setLevel(logging.ERROR)

    if providers:
        providers = [p.strip() for p in providers.split(",")]
        for p in providers:
            if not p in sitenames:
                raise click.BadParameter(f"{p}. Choose from {', '.join(sitenames)}")
    else:
        providers = sitenames

    if exclude:
        exclude = [e.strip() for e in exclude.split(",")]
        for e in exclude:
            if not e in sitenames:
                raise click.BadParameter(f"{e}. Choose from {', '.join(sitenames)}")
            else:
                if e in providers:
                    providers.remove(e)

    if os.name == 'nt':
        p, f = '', ''  # Emojis don't work in cmd
    else:
        p, f = '✅ ', '❌ '
    
    if verify:
        timeout = timeout + (3 * (v_tries - 1))
        
    threads = []
    matches = []

    for provider in providers:
        t = SiteThread(provider, anime, verify, v_tries, daemon=True)
        t.start()
        threads.append(t)

    for i, thread in enumerate(threads):
        try:
            click.echo(f"[{i+1} of {len(threads)}] Searching ", nl=False)
            click.secho(f"{thread.provider}", nl=False, fg="cyan")
            click.echo(f"... (CTRL-C to stop) : ", nl=False)
            thread.join(timeout=timeout)
            if not thread.is_alive():
                if not thread.exception:
                    if thread.search_result:
                        if not no_fuzzy:
                            ratio = fuzz.token_set_ratio(anime.lower(), thread.search_result.lower())
                        else:
                            ratio = 100
                        if ratio > 50:
                            matches.append([thread.provider, thread.search_result, ratio])
                            click.secho(p + "Works, anime found.", fg="green")
                            if prompt_found:
                                if print_results:
                                    click.echo(f"\n- - -{thread.provider}- - -\n\n{thread.search_result}")
                                confirm = click.confirm(f"Found anime in {thread.provider}. Keep seaching?", default=True)
                                if not confirm:
                                    break
                        else:
                            click.secho(p + "Works, anime not found.", fg="yellow")
                    else:
                        click.secho(p + "Works, anime not found.", fg="yellow")
                else:
                    logging.debug('Error occurred during testing.')
                    logging.debug(thread.exception)
                    if thread.search_result:
                        click.secho(f + "Not working: anime found, extraction failed.", fg="red")
                    else:
                        click.secho(f + "Not working.", fg="red")
            else:
                logging.debug('Timeout during testing.')
                click.secho(f + "Not working: Timeout. Use -t to specify longer waiting period.", fg="red")

        except KeyboardInterrupt:
            skip = click.confirm(f"\nSkip {thread.provider} and continue searching? (Press enter for Yes)", default=True)
            if not skip:
                break

    if print_results:
        click.echo("\n" + util.format_matches(matches))
    else:
        click.echo("\n" + "Test finished.")
    