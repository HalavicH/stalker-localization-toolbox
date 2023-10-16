#!/usr/bin/python3
#
# Dependancies
# pip install lxml langdetect

import glob
from lxml import etree
from langdetect import detect
import sys

INPUT_ENCODING = 'windows-1251'

def extract_text_from_xml(file_path):
    parser = etree.XMLParser(encoding=INPUT_ENCODING, remove_blank_text=True)
    tree = etree.parse(file_path, parser=parser)
    root = tree.getroot()
    texts = [elem.text for elem in root.xpath('//text') if elem.text and elem.text.strip()]
    return ' '.join(texts)


def check_language_in_dir(directory, target_language):
    xml_files = glob.glob(f'{directory}/**/*.xml', recursive=True)
    for xml_file in xml_files:
        all_text = extract_text_from_xml(xml_file)
        if all_text:  # Check if there is text to analyze
            detected_language = detect(all_text)
            print(f"File: {xml_file} detected as: {detected_language}")
            if detected_language != target_language:
                print(f'Translation needed for file: {xml_file} (Detected language: {detected_language})')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} <directory_path> <target_language>')
        sys.exit(1)

    directory_path, target_language = sys.argv[1:3]
    check_language_in_dir(directory_path, target_language)
