# from colorama import Fore, Back, init
from rich import get_console
# init(autoreset=False)
#
#
# # Generic methods
# def colorize_fore(obj, color: Fore) -> str:
#     return color + str(obj) + Fore.RESET
#
#
# def colorize_background(obj, color: Back) -> str:
#     return color + str(obj) + Back.RESET
#
#
# # Front methods
# def cf_black(obj):
#     return colorize_fore(obj, Fore.BLACK)
#
#
# def cf_red(obj):
#     return colorize_fore(obj, Fore.RED)
#
#
# def cf_green(obj):
#     return colorize_fore(obj, Fore.GREEN)
#
#
# def cf_yellow(obj):
#     return colorize_fore(obj, Fore.YELLOW)
#
#
# def cf_blue(obj):
#     return colorize_fore(obj, Fore.BLUE)
#
#
# def cf_magenta(obj):
#     return colorize_fore(obj, Fore.MAGENTA)
#
#
# def cf_cyan(obj):
#     return colorize_fore(obj, Fore.CYAN)
#
#
# def cf_white(obj):
#     return colorize_fore(obj, Fore.WHITE)
#
#
# """ Back methods """
#
#
# def cb_black(obj):
#     return colorize_fore(obj, Back.BLACK)
#
#
# def cb_red(obj):
#     return colorize_fore(obj, Back.RED)
#
#
# def cb_green(obj):
#     return colorize_fore(obj, Back.GREEN)
#
#
# def cb_yellow(obj):
#     return colorize_fore(obj, Back.YELLOW)
#
#
# def cb_blue(obj):
#     return colorize_fore(obj, Back.BLUE)
#
#
# def cb_magenta(obj):
#     return colorize_fore(obj, Back.MAGENTA)
#
#
# def cb_cyan(obj):
#     return colorize_fore(obj, Back.CYAN)
#
#
# def cb_white(obj):
#     return colorize_fore(obj, Back.WHITE)

from rich.console import Console

console = get_console()


# Generic methods
def cf(obj, color: str) -> str:
    return f"[{color}]{obj}[/{color}]"


def cb(obj, color: str) -> str:
    return f"[on {color}]{obj}[/on {color}]"


# Front methods
def cf_black(obj):
    return cf(obj, "black")


def cf_red(obj):
    return cf(obj, "red")


def cf_green(obj):
    return cf(obj, "green")


def cf_yellow(obj):
    return cf(obj, "yellow")


def cf_blue(obj):
    return cf(obj, "blue")


def cf_magenta(obj):
    return cf(obj, "magenta")


def cf_cyan(obj):
    return cf(obj, "cyan")


def cf_white(obj):
    return cf(obj, "white")


# Back methods
def cb_black(obj):
    return cb(obj, "black")


def cb_red(obj):
    return cb(obj, "red")


def cb_green(obj):
    return cb(obj, "green")


def cb_yellow(obj):
    return cb(obj, "yellow")


def cb_blue(obj):
    return cb(obj, "blue")


def cb_magenta(obj):
    return cb(obj, "magenta")


def cb_cyan(obj):
    return cb(obj, "cyan")


def cb_white(obj):
    return cb(obj, "white")
