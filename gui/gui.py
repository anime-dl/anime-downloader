import eel
from anime_downloader.sites import get_anime_class
from anime_downloader.config import Config
eel.init('web')

@eel.expose
def populate_dropdown():
    from anime_downloader.sites import ALL_ANIME_SITES
    providers = [i[1] for i in ALL_ANIME_SITES]
    eel.populate_dropdown(providers)


@eel.expose
def anime_search(query, provider):
    print('serching')
    print(query, provider)
    anime_cls = get_anime_class(provider)
    print(anime_cls)
    res = anime_cls.search(query)
    print(res)

    eel.populate_search([dict(title=i.title, url=i.url, poster=i.poster) for i in res])


@eel.expose
def get_animeinfo(url):
    print('getting info of: '+ url)
    anime = get_anime_class(url)(url)
    print(anime)
    return {
        'title': anime.title,
        'length': len(anime),
    }


@eel.expose
def get_config():
    return Config._CONFIG


eel.start('main.html', block=False)

while True:
    eel.sleep(1.0)
