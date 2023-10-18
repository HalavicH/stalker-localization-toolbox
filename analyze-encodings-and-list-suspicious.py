#!/usr/bin/python3

"""
Script for checking the encoding of XML files in a specified directory.
Dependencies:
- chardet
- colorama
- prettytable
Install dependencies using the following command:
pip3 install chardet colorama prettytable
"""

import argparse
import glob
import os
import threading
from concurrent.futures import ThreadPoolExecutor

import chardet
import colorama
from colorama import Fore
from prettytable import PrettyTable

# Constants
ALLOWED_ENCODINGS = ['windows-1251', 'ascii']
MAX_WORKERS = 8

colorama.init(autoreset=True)


def get_thread_color():
    thread_name = threading.current_thread().name
    thread_number = int(thread_name.split('_')[1])
    colors = [
        Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE,
        Fore.MAGENTA, Fore.CYAN, Fore.WHITE, Fore.LIGHTGREEN_EX
    ]
    color = colors[thread_number % len(colors)]
    return color


def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']


def check_encoding(file_path):
    thread_name = threading.current_thread().name
    color = get_thread_color()
    print(f"{color}[Thread {thread_name}] Processing file: {file_path}")
    encoding = detect_encoding(file_path)
    if encoding.lower() not in ALLOWED_ENCODINGS:
        return (file_path, encoding)
    return None


def process_files(path):
    if os.path.isdir(path):
        xml_files = glob.glob(f'{path}/**/**/*.xml', recursive=True)
    else:
        xml_files = [path]

    total_files = len(xml_files)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(check_encoding, xml_files))

    incorrect_encoding_files = [result for result in results if result is not None]

    print(f"Total files: {total_files}")
    if len(incorrect_encoding_files) == 0:
        print(Fore.GREEN + "No suspicious files. All good")
        return

    table = PrettyTable()
    table.field_names = ["File", "Encoding"]
    table.align = "l"

    unique_files = set(incorrect_encoding_files)
    sorted_files = sorted(unique_files, key=lambda x: x[1])
    for file_path, encoding in sorted_files:
        table.add_row([file_path, encoding])

    print(table)
    print(f"There are {len(incorrect_encoding_files)} suspicious files.")


def main():
    parser = argparse.ArgumentParser(description='Check encoding of XML files.')
    parser.add_argument('path', help='Path to the XML file or directory containing XML files.')
    args = parser.parse_args()
    process_files(args.path)


if __name__ == '__main__':
    main()
