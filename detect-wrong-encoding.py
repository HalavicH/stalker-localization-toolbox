#!/usr/bin/python3

import glob
import chardet
from lxml import etree
from prettytable import PrettyTable

allowed_encodings = ['windows-1251', 'ascii']

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def process_files(directory):
    incorrect_encoding_files = []
    xml_files = glob.glob(f'{directory}/**/**/*.xml', recursive=True)

    for file_path in xml_files:
        print(f"Processing file: {file_path}")

        encoding = detect_encoding(file_path)
        if encoding.lower() not in allowed_encodings:
            incorrect_encoding_files.append((file_path, encoding))

    # Create a PrettyTable object
    table = PrettyTable()
    table.field_names = ["File", "Encoding"]  # Set the column headers
    table.align = "l"  # Set text alignment to left for all columns

    sorted_files = sorted(incorrect_encoding_files, key=lambda x: x[1])

    for file_path, encoding in sorted_files:
        table.add_row([file_path, encoding])  # Add a row to the table for each file

    print(table)  # Print the table

    # for file_path, encoding in incorrect_encoding_files:
        # print(f"File: {file_path} | Encoding: {encoding}")

    print(f"Processed {len(incorrect_encoding_files)} files.")

# Replace 'your_directory' with the path to the directory containing your XML files
process_files('.')
