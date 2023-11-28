#!/usr/bin/python3

import os
import re
import sys


def parse_po_file(po_file_path):
    with open(po_file_path, 'r', encoding='utf-8') as file:
        po_contents = file.readlines()
    po_keys = {}
    key, value = None, None
    for line in po_contents:
        if line.startswith('msgid'):
            key = line.strip().split('msgid ', 1)[1]
        elif line.startswith('msgstr'):
            value = line.strip().split('msgstr ', 1)[1]
            if key and key != '""':
                po_keys[key] = value
                key, value = None, None
    return po_contents, po_keys


def find_and_update_keys(directory, po_file_path):
    # Corrected pattern to match both single and double-quoted strings
    pattern = re.compile(r"trn\('([^']*)'|trn\(\"([^\"]*)\"\)")
    _, existing_keys = parse_po_file(po_file_path)
    all_keys = []
    new_keys = {}

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                with open(path, 'r') as f:
                    content = f.read()
                    matches = pattern.findall(content)
                    for key_tuple in matches:
                        key = next(s for s in key_tuple if s)  # Get the non-empty string from the tuple
                        formatted_key = '"' + key.replace('"', '\\"') + '"'
                        all_keys.append(formatted_key)
                        if formatted_key not in existing_keys:
                            new_keys[f'msgid {formatted_key}\n'] = f'msgstr {formatted_key}\n\n'

    with open(po_file_path, 'a', encoding='utf-8') as po_file:
        for key, msgstr in new_keys.items():
            print(f"{key} is absent. Adding...")
            po_file.write(key + msgstr)

    # Check for unused keys
    for key in existing_keys:
        if key not in all_keys:
            print(f"Unused key detected. Key: {key}, line: {existing_keys[key]}")


if len(sys.argv) != 3:
    print("Usage: python script.py [directory] [po_file_path]")
else:
    find_and_update_keys(sys.argv[1], sys.argv[2])
