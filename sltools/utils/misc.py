import os
import traceback
from importlib.metadata import version

import requests
from rich.table import Table

from sltools.utils.colorize import *


def get_term_width():
    try:
        return os.get_terminal_size().columns
    except Exception as e:
        return 160


def create_table(columns, title=None, border_style="light_slate_grey"):
    table = Table(title=title, border_style=border_style)

    for column in columns:
        table.add_column(column, justify="left")

    return table


def color_lang(lang):
    lang_to_colored = {
        "uk": cf_green("uk"),
        "ru": cf_red("ru"),
        "en": cf_blue("en"),
        "pl": cf_cyan("pl"),
        "fr": cf_yellow("fr"),
        "sp": cf_magenta("sp"),
        "Unknown": cf_red("Unknown"),
    }

    colored = lang_to_colored.get(lang)
    if colored is None:
        colored = lang
    return colored


def exception_originates_from(func_name, exception):
    """
    Checks if the exception originated from the given function or its children.

    Parameters:
    - func_name (str): The name of the function to check against.
    - exception (Exception): The caught exception.

    Returns:
    - bool: True if the exception originated from the function or its children, False otherwise.
    """
    stack_trace = traceback.extract_tb(exception.__traceback__)
    for frame in stack_trace:
        if frame.name == func_name:
            return True
    return False


def check_for_update():
    current_version = version('sltools')
    response = requests.get(f'https://pypi.org/pypi/sltools/json')
    if response.ok:
        latest_version = response.json()['info']['version']
        if current_version < latest_version:
            return (f'\n☢️\\[[blue]notice[/blue]] A new release of [cyan]sltools[/cyan] is available: '
                    f'[red]{current_version}[/red] -> [green]{latest_version}[/green]. '
                    f'To upgrade run [green]pip install sltools --upgrade[/green]')
        else:
            return '[bright_black]You are using the latest version of sltools.[/bright_black]'
    else:
        return f'Failed to check for updates: {response.text}'


def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError(f"{obj} is not instance of set. Don't know how to default it")


def check_paths_exist(paths):
    return all(os.path.exists(path) for path in paths)


def remove_invalid_paths(paths):
    return [path for path in paths if os.path.exists(path)]
