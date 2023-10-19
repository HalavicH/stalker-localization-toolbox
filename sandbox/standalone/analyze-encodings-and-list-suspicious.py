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


def check_encoding(file_path, i):
    # thread_name = threading.current_thread().name
    # color = get_thread_color()
    # print(f"{color}[Thread {thread_name}] Processing file #{i}: {file_path}")
    # print(" " * 100,end='\r')
    print(Fore.GREEN + f"  Processing file #{i}" ,end='\r')
    encoding = detect_encoding(file_path)
    if encoding.lower() not in ALLOWED_ENCODINGS:
        return (file_path, encoding, is_windows_1251_compatible(file_path))
    return None


def is_windows_1251_compatible(file_path):
    try:
        # Attempt to decode the file with windows-1251 encoding
        with open(file_path, 'rb') as file:
            data = file.read()
            decoded_text = data.decode('windows-1251')
            return True  # Successfully decoded with windows-1251
    except UnicodeDecodeError:
        return False  # Decoding error occurred, not compatible with windows-1251


def process_files(path):
    if os.path.isdir(path):
        xml_files = set(glob.glob(f'{path}/**/*.xml', recursive=True))
    else:
        xml_files = [path]

    total_files = len(xml_files)
    print(f"Total files: {total_files}")

    # futures = []
    # with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    #     for i, xml_file in enumerate(xml_files):
    #         # print(f"Submitted file [{i}]: {xml_file}")
    #         futures.append(executor.submit(check_encoding, xml_file, i))
    #     # results = list(executor.map(check_encoding, xml_files))
    #
    # incorrect_encoding_files = []
    # for i in range(0, len(futures)):
    #     # print(f"Waiting for future {i}")
    #     result = futures[i].result()
    #     if result is not None:
    #         incorrect_encoding_files.append(result)

    # with ThreadPoolExecutor(max_workers=1) as executor:
    #     results = list(executor.map(check_encoding, xml_files))

    # incorrect_encoding_files = [result for result in results if result is not None]

    incorrect_encoding_files = []
    for i, file in enumerate(xml_files):
        # print(f"Waiting for future {i}")
        result = check_encoding(file, i)
        if result is not None:
            incorrect_encoding_files.append(result)

    print(" " * 80)

    if len(incorrect_encoding_files) == 0:
        print(Fore.GREEN + "No suspicious files. All good")
        return

    table = PrettyTable()
    table.field_names = ["File", "Guessed Encoding", "Compatible"]
    table.align = "l"

    unique_files = set(incorrect_encoding_files)

    sorted_files = sorted(unique_files, key=lambda x: x[1])
    for file_path, encoding, compatible in sorted_files:
        if compatible:
            compatible_str = Fore.GREEN + "Yes" + Fore.RESET
        else:
            compatible_str = Fore.RED + "No!" + Fore.RESET

        table.add_row([file_path, encoding, compatible_str])

    print(table)
    print(f"There are {len(unique_files)} suspicious files.")


def main():
    parser = argparse.ArgumentParser(description='Check encoding of XML files.')
    parser.add_argument('path', help='Path to the XML file or directory containing XML files.')
    args = parser.parse_args()
    process_files(args.path)


if __name__ == '__main__':
    main()
