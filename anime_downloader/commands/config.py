import click
from tabulate import tabulate
from anime_downloader.config import Config

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
        newVal = click.prompt(f"Input new value for {keys[val]}", type = str)

        #Normal strings cause an error
        try:
            newVal = eval(newVal)
        except SyntaxError:
            pass
        
        if type(newVal) != type(data[keys[val]]):
            choice = click.confirm(f"{newVal} appears to be of an incorrect type. Continue")

            if not choice:
                exit()

        data[keys[val]] = newVal

traverse_json(data)
Config._CONFIG = data
Config.write()
exit()
