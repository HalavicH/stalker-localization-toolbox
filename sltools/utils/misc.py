import os
import traceback
from importlib.metadata import version

from langdetect import detect_langs

from sltools.utils.plain_text_utils import fold_text

import requests
from rich.table import Table

from sltools.utils.colorize import *
from sltools.utils.lang_utils import _tr


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
    stack_trace = traceback.extract_tb(exception.__traceback__)
    for frame in stack_trace:
        if frame.name == func_name:
            return True
    return False


def check_for_update():
    current_version = version('sltools')
    response = requests.get('https://pypi.org/pypi/sltools/json')
    if response.ok:
        latest_version = response.json()['info']['version']
        if current_version < latest_version:
            return (_tr("\n☢️\\[[blue]notice[/blue]] A new release of [cyan]sltools[/cyan] is available: "
                        "[red]%s[/red] -> [green]%s[/green]. "
                        "To upgrade run [green]pip install sltools --upgrade[/green]") % (
                        current_version, latest_version))
        else:
            return _tr('[bright_black]You are using the latest version of sltools.[/bright_black]') + " " + current_version
    else:
        return _tr('Failed to check for updates: %s') % response.text


def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError(_tr("%s is not instance of set. Don't know how to default it") % obj)


def check_paths_exist(paths):
    return all(os.path.exists(path) for path in paths)


def remove_invalid_paths(paths):
    return [path for path in paths if os.path.exists(path)]


def detect_language(text, possible_languages=["uk", "en", "ru", "fr", "es"]):
    detections = detect_langs(fold_text(text))
    for detection in detections:
        lang, confidence = str(detection).split(':')
        if lang in possible_languages:
            return lang, float(confidence)
    return "Unknown", 0.0


def create_equal_length_comment_line(text, char='='):
    return char * len(text)


### Misc command
def check_deepl_tokens_usage(token_list):
    columns = [_tr("Token"), _tr("Plan"), _tr("Used"), _tr("Available"), _tr("Used %")]
    table = create_table(columns, title=_tr("DeepL Token Usage"), border_style="blue")

    api_url = 'https://api-free.deepl.com/v2/usage'

    for token in token_list:
        headers = {"Authorization": f"DeepL-Auth-Key {token}"}

        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            json_data = response.json()

            if 'character_count' in json_data and 'character_limit' in json_data:
                plan = json_data['character_limit']
                used = json_data['character_count']
                used_percentage = (used / plan) * 100 if plan != 0 else 0
                available = plan - used
                table.add_row(
                    token,
                    f"{plan:,}".replace(",", " ").rjust(7),
                    f"{used:,}".replace(",", " ").rjust(7),
                    f"{available:,}".replace(",", " ").rjust(7),
                    generate_gradient_usage_bar(used_percentage, 30)
                )
            else:
                table.add_row(token, cf_red(_tr("Error")), "N/A", "N/A", "N/A")

        except requests.exceptions.RequestException as e:
            table.add_row(token, cf_red(_tr("Error")), "N/A", "N/A", "N/A")

    get_console().print(table)


def generate_gradient_usage_bar(percentage, bar_length=20):
    """
    Generates a usage bar string with color gradient based on the percentage value.

    Args:
        percentage (float): The percentage of usage.
        bar_length (int): The total length of the bar in characters.

    Returns:
        str: A string representing the gradient usage bar.
    """
    # Define the gradient range from green to red
    gradient_range = [
        "#00ff00",  # Green
        "#40ff00",
        "#80ff00",
        "#bfff00",
        "#ffff00",  # Yellow
        "#ffbf00",
        "#ff8000",
        "#ff4000",
        "#ff0000"  # Red
    ]

    # Calculate the index for the color based on the percentage
    color_index = int((percentage / 100) * (len(gradient_range) - 1))
    bar_color = gradient_range[color_index]

    # Calculate the number of characters that should be filled
    filled_length = int(round(bar_length * percentage / 100))

    # Create the bar string
    bar = f"[{bar_color}]" + "━" * filled_length + f"╸[grey53]" + "━" * (bar_length - filled_length) + f" [/grey53][{bar_color}]{percentage:.2f}%[/{bar_color}]"

    return bar
