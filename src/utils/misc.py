import os
import traceback

from rich.table import Table

from src.utils.colorize import *


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
