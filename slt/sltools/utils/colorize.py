from colorama import Fore, Back, init

init(autoreset=False)


# Generic methods
def colorize_fore(obj, color: Fore) -> str:
    return color + str(obj) + Fore.RESET


def colorize_background(obj, color: Back) -> str:
    return color + str(obj) + Back.RESET


# Front methods
def cf_black(obj):
    return colorize_fore(obj, Fore.BLACK)


def cf_red(obj):
    return colorize_fore(obj, Fore.RED)


def cf_green(obj):
    return colorize_fore(obj, Fore.GREEN)


def cf_yellow(obj):
    return colorize_fore(obj, Fore.YELLOW)


def cf_blue(obj):
    return colorize_fore(obj, Fore.BLUE)


def cf_magenta(obj):
    return colorize_fore(obj, Fore.MAGENTA)


def cf_cyan(obj):
    return colorize_fore(obj, Fore.CYAN)


def cf_white(obj):
    return colorize_fore(obj, Fore.WHITE)


""" Back methods """


def cb_black(obj):
    return colorize_fore(obj, Back.BLACK)


def cb_red(obj):
    return colorize_fore(obj, Back.RED)


def cb_green(obj):
    return colorize_fore(obj, Back.GREEN)


def cb_yellow(obj):
    return colorize_fore(obj, Back.YELLOW)


def cb_blue(obj):
    return colorize_fore(obj, Back.BLUE)


def cb_magenta(obj):
    return colorize_fore(obj, Back.MAGENTA)


def cb_cyan(obj):
    return colorize_fore(obj, Back.CYAN)


def cb_white(obj):
    return colorize_fore(obj, Back.WHITE)
