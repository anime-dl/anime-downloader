import eel
from anime_downloader.sites import get_anime_class
from anime_downloader.config import Config
from anime_downloader import util
from anime_downloader.sites.anime import AnimeEpisode
import subprocess
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
    global anime
    print('getting info of: '+ url)
    anime = get_anime_class(url)(url)
    print(anime)
    print(anime[0].source().stream_url)
    return {
        'title': anime.title,
        'length': len(anime),
    }

def play_mirror_file(player, title, file, ):
    if player == 'mpv':
        p = subprocess.Popen([
            player,
            '--title={}'.format(title),
            file,
            ])
    else:
        p = subprocess.Popen([ player, file
            ])
    p.wait()


    
@eel.expose
def download(start, end):
    episodes = util.parse_ep_str(anime, start + ":" + end)
    for i in episodes:
        # Fix util-prase episode range
        external_downloader = Config['dl']['external_downloader']
        file_format = Config['dl']['file_format']
        download_dir = Config['dl']['download_dir']
        speed_limit= Config['dl']['speed_limit']
        util.external_download(external_downloader, i, file_format,path=download_dir, speed_limit=speed_limit)

@eel.expose
def load_vlc(start, end): 
    #print(anime)
    #episodes = anime['_episode_urls']
    #test = AnimeEpisode(episodes[0][1], anime['quality'], anime['_fallback_qualities'])
    episodes = util.parse_ep_str(anime, start+':'+end)
    text = "#EXTM3U\n"
    for i in episodes:
        print(i.__dict__)

    for i in episodes:
        text += f"#EXTINF:,Episode {(i.ep_no)}\n" 
        text += i.source().stream_url + "\n"
    text_file = open("MirrorList.m3u8", "w")
    text_file.write(text)
    text_file.close()
    print("Playing m3u8 file")
    play_mirror_file("mpv",anime.title,"MirrorList.m3u8")
     


@eel.expose
def get_config():
    return Config._CONFIG


eel.start('main.html', block=False)

while True:
    eel.sleep(1.0)
