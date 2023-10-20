import os
import threading

from colorama import Fore, init

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
    return os.get_terminal_size().columns