#!/usr/bin/python3

import os
import sys


def filter_lines(path, filters):
    match = True if len(filters) == 0 else False
    include_filters = filter(lambda f: '!' not in f, filters)
    exclude_filters = filter(lambda f: '!' in f, filters)

    # Exclude where filter matches
    for filter_str in include_filters:
        if filter_str in path:
            match = True
            break

    # Exclude where !filter match
    for filter_str in exclude_filters:
        if filter_str[1:] not in path:
            continue
        else:
            match = False

    if not match:
        print("Skipping: " + path.strip())

    return match


def process_file_tree(input_file_path, filters):
    # Output file will be in the same directory as the input file
    filename = os.path.basename(input_file_path)
    output_file_path = os.path.join(os.path.dirname(input_file_path), f'{filename}-real-paths.txt')

    with open(input_file_path, 'r', encoding='utf-8') as input_file, \
            open(output_file_path, 'w', encoding='utf-8') as output_file:

        filtered_lines = filter(lambda path: filter_lines(path, filters), input_file)

        for line in filtered_lines:
            # Splitting the line to separate the file path and the mod info
            parts = line.strip().split('\t')
            if len(parts) == 2:
                file_path, mod_info = parts
                mod_name = mod_info.strip().strip('()')
                # Remove the 'Data' folder and construct the real file path
                file_path = file_path.replace('Data\\', '')
                real_path = f".\\mods\\{mod_name}\\{file_path}"

                output_file.write(real_path + '\n')

    return output_file_path


# Example usage
input_file_path = 'file-tree-with-ukr-overrides-eng.txt'
# filters = ['gamedata', 'appdata']
filters = ['gamedata\\configs\\text\\eng', '!Ukrainian']

output_path = process_file_tree(input_file_path, filters)
print(f"Converted file paths saved to: {output_path}")
