import os
import threading
import traceback

from prettytable import PrettyTable

from src.utils.colorize import *

init(autoreset=True)


def get_thread_color():
    thread_name = threading.current_thread().name
    thread_number = int(thread_name.split('_')[1])
    colors = [
        Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE,
        Fore.MAGENTA, Fore.CYAN, Fore.WHITE, Fore.LIGHTGREEN_EX
    ]
    color = colors[thread_number % len(colors)]
    return color


def get_term_width():
    try:
        return os.get_terminal_size().columns
    except Exception as e:
        return 160


def create_pretty_table(columns, title=None):
    table = PrettyTable()
    if title is not None:
        table.title = title
    table.field_names = columns
    table.align = 'l'
    table.border = True

    # Basic lines
    table.vertical_char = u'\u2502'  # Vertical line
    table.horizontal_char = u'\u2500'  # Horizontal line
    table._horizontal_align_char = None  # Default is None, setting it explicitly for clarity
    table.junction_char = u'\u253C'  # Plus

    # Corner characters for smooth edges
    table.top_left_junction_char = u'\u256D'  # Rounded top-left corner
    table.top_right_junction_char = u'\u256E'  # Rounded top-right corner
    table.bottom_left_junction_char = u'\u2570'  # Rounded bottom-left corner
    table.bottom_right_junction_char = u'\u256F'  # Rounded bottom-right corner

    # Junction characters for T-junctions
    table.top_junction_char = u'\u252C'  # T-junction facing down
    table.bottom_junction_char = u'\u2534'  # T-junction facing up
    table.left_junction_char = u'\u251C'  # T-junction facing right
    table.right_junction_char = u'\u2524'  # T-junction facing left
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
