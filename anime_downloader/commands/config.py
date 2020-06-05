import json
import os
import sys
import click
import time
import logging
from tabulate import tabulate
from anime_downloader.sites import ALL_ANIME_SITES
from anime_downloader.config import Config
from anime_downloader import config

logger = logging.getLogger(__name__)
sitenames = [*config.DEFAULT_CONFIG["siteconfig"]]

data = Config._CONFIG

def create_table(_list):
    newList = [(x, y) for x, y in zip(range(1,len(_list) + 1), _list)]
    table = tabulate(newList, tablefmt = "psql")
    table = "\n".join(table.split("\n")[::-1])
    return table

def traverse_json(data):
    click.clear()
    keys = [*data.keys()]
    click.echo(create_table(keys))
    val = click.prompt("Select Option", type = int, default = 1) - 1
    
    if type(data[keys[val]]) == dict:
        traverse_json(data[keys[val]])
    else:
        click.echo(f"Current value: {data[keys[val]]}")
        data[keys[val]] = click.prompt(f"Input new value for {keys[val]}", type = type(data[keys[val]]))
        return data

traverse_json(data)
Config._CONFIG = data
Config.write()
=======
sitenames = [v[1] for v in ALL_ANIME_SITES]
def clear():    
    os.system('cls||clear')
def get_config(): #can't import config directly because of circular import
    APP_NAME = 'anime downloader'
    with open(os.path.join(click.get_app_dir(APP_NAME), 'config.json')) as json_file:
        data = json.load(json_file)
    return data


def create_table(values, option = "setting"):
    if values == str:
        val = click.prompt(f'Input the choice here or choose {option} (0 to go back): ', type=str, default="0")
        clear()
        return None if val == "0" else val
    else:
        table = [[a+1,[b for b in values][a]] for a in range(len(values))]
        clear()
        table = tabulate(table, tablefmt='psql')
        table = '\n'.join(table.split('\n')[::-1])
        click.echo(table)
        val = click.prompt(f'Choose {option} (0 to go back): ', type=int, default=1, err=True)
        return None if val == 0 else [a for a in values][val-1] 


#If you are having trouble to understand how this works then take a look at the link below
#https://stackoverflow.com/questions/13687924/setting-a-value-in-a-nested-python-dictionary-given-a-list-of-indices-and-value
def nested_set(dictionary, keys, value, create_missing=False): 
    d = dictionary
    for key in keys[:-1]:
        if key in d:
            d = d[key]
        elif create_missing:
            d = d.setdefault(key, {})
        else:
            return dic
    if keys[-1] in d or create_missing:
        d[keys[-1]] = value
    return dictionary

layout = {
    'Default provider settings':{
        'Quality':['720p','1080p'],
        'Provider':sitenames
    },
    'General settings':{
        'Use aria2 for torrents':[True,False],
        'Download directory':str,
        'Skip Download':[True, False],
        'Player':['mpv', 'vlc'],
        'File format':["{anime_title}/{anime_title}_{ep_no}", "{anime_title}/{anime_title}-{ep_no}",\
        "{anime_title}/{anime_title}/{anime_title}-{ep_no}", "{anime_title}/{anime_title}/{ep_no}"]
    },
    'Advanced Settings':{
        'external_downloader':str,
        'chunk size':['5' ,'10', '15', '20', '30'],
    #    'browser':['chrome', 'firefox'],
    #    'browser executable path':str,
    #    'webdriver executable path':str,
    },
}

data = get_config()

#Links layout selection to data location
connected = { 
    'Quality':[['dl','quality'],data['dl']['quality']],
    'Provider':[['dl','provider'],data['dl']['provider']],
    'Use aria2 for torrents':[['dl','aria2c_for_torrents'],data['dl']['aria2c_for_torrents']],
    'Download directory':[['dl','download_dir'],data['dl']['download_dir']],
    'Skip Download':[['dl','skip_download'],data['dl']['skip_download']],
    'Player':[['dl','player'],data['dl']['player']],
    'File format':[['dl','file_format'],data['dl']['file_format']],
    'external_downloader':[['dl', 'external_downloader'], data['dl']['external_downloader']],
    'chunk size':[['dl', 'chunk_size'], data['dl']['chunk_size']]
    # , 'browser':[['dl', 'selescrape_browser'], data['dl']['selescrape_browser']]
    # ,'browser executable path':[['dl', 'selescrape_browser_executable_path'], data['dl']['selescrape_browser_executable_path']]
    # ,'webdriver executable path':[['dl', 'selescrape_driver_binary_path'], data['dl']['selescrape_driver_binary_path']]
            }
clear()
prev_choice = None
location = []
while True:
    values = layout
    for a in location:
        values = values[a]

    choice = create_table(values)
    
    if choice == None:
        if len(location) == 0:
            break
        else:
            location = location[:-1]
            continue
    clear()
    if type(values) != dict:
        if prev_choice in connected:
            connected[prev_choice][1] = choice
            location = []
    else:
        prev_choice = choice
        values = None if choice == None else values[choice]
        if choice != None:
            location.append(str(choice))
    clear()
for a in connected: #Saves the data
    data = (nested_set(data,connected[a][0],connected[a][1]))
APP_NAME = 'anime downloader'
with open(os.path.join(click.get_app_dir(APP_NAME), 'config.json'), 'w') as json_file:
        json.dump(data, json_file)
exit()
