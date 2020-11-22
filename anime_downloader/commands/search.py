import logging

import click
from fuzzywuzzy import fuzz

from anime_downloader import util
from anime_downloader.__version__ import __version__
from anime_downloader.sites import ALL_ANIME_SITES

logger = logging.getLogger(__name__)

echo = click.echo
sitenames = [v[1] for v in ALL_ANIME_SITES]

@click.command()
@click.argument('anime')
@click.option(
    '--full-search', '-f', is_flag=True,
    help='Don\'t ask to stop searching on anime match.')
@click.option(
    '-p', '--providers',
    help='Limit search to specific provider(s) separated by a comma.'
)
@click.option(
    '-e', '--exclude',
    help='Providers to exclude separated by a comma.'
)

@click.pass_context
def command(ctx, anime, full_search, providers, exclude):
    """ Search for the anime across all providers and return matching providers.
    """ 
    util.print_info(__version__)
    
    if providers:
        providers = [p.strip() for p in providers.split(",")]
        for p in providers:
            if not p in sitenames:
                raise click.BadParameter(f"{p}. Choose from {', '.join(sitenames)}")
    else:
        providers = sitenames
        providers.remove("kisscartoon") #uses selenium

    if exclude:
        exclude = [e.strip() for e in exclude.split(",")]
        for e in exclude:
            if not e in sitenames:
                raise click.BadParameter(f"{e}. Choose from {', '.join(sitenames)}")
            else:
                providers.remove(e)

    matches = []

    for i, provider in enumerate(providers):
        try:
            click.echo(f"[{i+1} of {len(providers)}] Searching ", nl=False)
            click.secho(f"{provider}", nl=False, fg="yellow")
            click.echo(f"... (CTRL-C to stop the search) : ", nl=False)
            try:
                search_result = util.search_only(anime, provider)
            except KeyboardInterrupt:
                raise
            except:
                search_result = None
            if search_result:
                ratio = fuzz.token_set_ratio(anime.lower(), search_result.lower())
                if ratio > 50:
                    matches.append([provider, search_result, ratio])
                    click.secho("Found!", fg="green")
                    if not full_search:
                        click.echo(f"\n- - -{provider}- - -\n\n{search_result}")
                        confirm = click.confirm(f"Found anime in {provider}. Keep seaching? (use -f / --full-search to disable this prompt)")
                        if not confirm:
                            break
                else:
                     click.secho("Not found.", fg="red")
            else:
                click.secho("Not found.", fg="red")
                            
        except KeyboardInterrupt:
            skip = click.confirm(f"\nSkip {provider} and continue searching?", default=True)
            if not skip:
                break

    click.echo("\n" + util.format_matches(matches))