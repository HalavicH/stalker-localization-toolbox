#!/usr/bin/python3

import glob
import threading

import chardet
import colorama
from colorama import Fore
from prettytable import PrettyTable
from concurrent.futures import ThreadPoolExecutor

allowed_encodings = ['windows-1251', 'ascii']

colorama.init(autoreset=True)
def get_thread_color():
    thread_name = threading.current_thread().name
    # Extract the thread number from the thread name
    thread_number = int(thread_name.split('_')[1])
    # List of colors from colorama.Fore
    colors = [
        Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE,
        Fore.MAGENTA, Fore.CYAN, Fore.WHITE, Fore.LIGHTGREEN_EX
    ]
    # Use the thread number to index into the list of colors
    # Use modulo to ensure the index is within bounds
    color = colors[thread_number % len(colors)]
    return color

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']


def check_encoding(file_path):
    thread_name = threading.current_thread().name  # Get the name of the current thread
    color = get_thread_color()

    print(f"{color}[Thread {thread_name}] Processing file: {file_path}")
    encoding = detect_encoding(file_path)
    if encoding.lower() not in allowed_encodings:
        return (file_path, encoding)
    return None  # Return None if the file encoding is allowed


def process_files(directory):
    xml_files = glob.glob(f'{directory}/**/**/*.xml', recursive=True)
    total_files = len(xml_files)

    incorrect_encoding_files = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(check_encoding, xml_files))

    incorrect_encoding_files = [result for result in results if result is not None]

    # Create a PrettyTable object
    table = PrettyTable()
    table.field_names = ["File", "Encoding"]  # Set the column headers
    table.align = "l"  # Set text alignment to left for all columns

    unique_files = set(incorrect_encoding_files)
    sorted_files = sorted(unique_files, key=lambda x: x[1])
    for file_path, encoding in sorted_files:
        table.add_row([file_path, encoding])  # Add a row to the table for each file

    print(table)  # Print the table

    print(f"Processed {len(incorrect_encoding_files)} files.")
    print(f"Total files: {total_files}")

# Replace 'your_directory' with the path to the directory containing your XML files
process_files('.')
