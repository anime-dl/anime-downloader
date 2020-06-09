import click
from tabulate import tabulate
from anime_downloader.config import Config

data = Config._CONFIG

def create_table(_list, previous):
    newList = list(enumerate(_list, 1))
    headers = ['SlNo', f'{previous} settings'.strip()]
    table = tabulate(newList, headers, tablefmt = "psql")
    table = "\n".join(table.split("\n")[::-1])
    return table

def traverse_json(data, previous=''):
    click.clear()
    keys = list(data.keys())
    click.echo(create_table(keys, previous))
    val = click.prompt("Select Option", type = int, default = 1) - 1
    
    if type(data[keys[val]]) == dict:
        traverse_json(data[keys[val]], keys[val])
    else:
        click.echo(f"Current value: {data[keys[val]]}")
        newVal = click.prompt(f"Input new value for {keys[val]}", type = str)

        #Normal strings cause an error
        try:
            newVal = eval(newVal)
        except (SyntaxError, NameError) as e:
            pass
        
        if type(newVal) != type(data[keys[val]]):
            choice = click.confirm(f"{newVal} appears to be of an incorrect type. Continue")

            if not choice:
                exit()
            elif data[keys[val]] is not None:
                try:
                    newVal = type(data[keys[val]])(newVal)
                except TypeError:
                    click.echo(f"'{newVal}' could not be converted to the correct type")
                    exit()

        data[keys[val]] = newVal

@click.command()
def command():
    """
    Presents a list based on the keys in the dictionary.
    If the value of said key is not a dictionary, the user will be able to edit the value.
    """
    traverse_json(data)
    Config._CONFIG = data
    Config.write()
    exit()
