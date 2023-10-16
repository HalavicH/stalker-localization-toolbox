#!/usr/bin/python3
#
# Dependancies
# pip install lxml googletrans==4.0.0-rc1 colorama

import os
import re
from lxml import etree
from googletrans import Translator
from colorama import Fore
from langdetect import detect

# Constants for configuration
INPUT_ENCODING = 'windows-1251'
OUTPUT_ENCODING = 'windows-1251'

# Define a mapping of placeholders to unique tokens
placeholder_mapping = {
    '%s': 'PLACEHOLDER_PERCENT_S',
    '%c': 'PLACEHOLDER_PERCENT_C',
    '\\n': '\n',
    # Add any other static placeholders and their corresponding tokens here
}

def translate_xml(input_path, from_lang, to_lang):
    # Create output directory if not exists
    output_dir = os.path.join('./translated', os.path.dirname(input_path[2:]))
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse the XML, preserving comments
    parser = etree.XMLParser(encoding=INPUT_ENCODING, remove_blank_text=True)
    tree = etree.parse(input_path, parser=parser)
    root = tree.getroot()
    
    translator = Translator()
    
    # Translate text inside <text> tags
    for text_elem in root.xpath('//text'):
        original_text = text_elem.text
        if original_text:
            process_text_block(from_lang, original_text, text_elem, to_lang, translator)

    # Write the translated XML to the output path
    output_path = os.path.join(output_dir, os.path.basename(input_path))
    with open(output_path, 'wb') as f:
        f.write(etree.tostring(root, pretty_print=True, encoding=OUTPUT_ENCODING, xml_declaration=True))

    # Polish the XML to have 4-space indentations and a newline before comments
    with open(output_path, 'r', encoding=OUTPUT_ENCODING) as f:
        xml_content = f.read()

    xml_content = xml_content.replace('  ', '    ').replace('--><', '-->\n<')
    
    with open(output_path, 'w', encoding=OUTPUT_ENCODING) as f:
        f.write(xml_content)


def process_text_block(from_lang, original_text, text_elem, to_lang, translator):
    print("")
    # Find and replace dynamic placeholders ($$...$$) with unique tokens
    dynamic_placeholders = re.findall(r'\$\$.*?\$\$', original_text)
    for idx, placeholder in enumerate(dynamic_placeholders, start=1):
        token = f'PLACEHOLDER_DYNAMIC_{idx}'
        placeholder_mapping[placeholder] = token

    # Replace placeholders with tokens in the original text
    guarded_text = original_text
    for placeholder, token in placeholder_mapping.items():
        guarded_text = guarded_text.replace(placeholder, token)

    print("Guarded:    " + guarded_text)

    # Translate the text with tokens
    translated_text = translator.translate(guarded_text, src=from_lang, dest=to_lang).text
    print("Translated: " + translated_text)

    # Restore original placeholders in the translated text
    restored_text = translated_text
    for placeholder, token in placeholder_mapping.items():
        restored_text = restored_text.replace(token, placeholder)

    print("Unguarded:  " + Fore.CYAN + restored_text + Fore.RESET)
    text_elem.text = restored_text

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 4:
        print(f'Usage: {sys.argv[0]} <input_xml_path> <from_lang> <to_lang>'),
        sys.exit(1)
    
    input_path, from_lang, to_lang = sys.argv[1:4]
    translate_xml(input_path, from_lang, to_lang)
