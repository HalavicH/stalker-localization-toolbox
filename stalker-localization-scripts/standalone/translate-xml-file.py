#!/usr/bin/python3
#
# Dependancies
# pip install lxml googletrans==4.0.0-rc1 colorama

import os
import re
import time

from lxml import etree
from googletrans import Translator
from colorama import Fore
import requests
from langdetect import detect_langs

# Constants for configuration
INPUT_ENCODING = 'windows-1251'
OUTPUT_ENCODING = 'windows-1251'

# Define a mapping of placeholders to unique tokens
placeholder_mapping = {
    '%s': 'PLACEHOLDER_PERCENT_S',
    '%c': 'PLACEHOLDER_PERCENT_C',
    # '\\n': '\n',
    # Add any other static placeholders and their corresponding tokens here
}

API_KEY = 'c31842ed-.............-468770f60f2d:fx'


def translate_deepl(text, target_language, src_language=None):
    url = 'https://api-free.deepl.com/v2/translate'
    headers = {
        'Authorization': f'DeepL-Auth-Key {API_KEY}'
    }
    data = {
        'text': text,
        'target_lang': target_language.upper(),
    }
    if src_language:
        data['source_lang'] = src_language.upper()

    response = requests.post(url, headers=headers, data=data)
    response_json = response.json()

    if response.status_code != 200:
        raise Exception(f'Error: {response_json.get("message", "API request failed")}')

    translated_text = response_json['translations'][0]['text']
    guessed_language = response_json['translations'][0]['detected_source_language']
    if guessed_language is not None:
        print(Fore.BLUE + "DeepL"+ Fore.RESET + " guessed lang: " + guessed_language)

    return translated_text


def detect_language(text, possible_languages=["uk", "en", "ru", "fr", "es"]):
    detections = detect_langs(text)
    for detection in detections:
        lang, confidence = str(detection).split(':')
        if lang in possible_languages:
            return lang, float(confidence)
    return None, 0.0


def translate_xml(input_path, from_lang, to_lang, override):
    if override.lower() == "y":
        print(Fore.YELLOW + "\nWARNING! Override mode is on. Source file will be overriden!\n" + Fore.RESET)
        output_path = input_path
        time.sleep(1)
    else:
        output_dir = os.path.join('./translated', os.path.dirname(input_path))
        # Create output directory if not exists
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join('./translated', input_path)

    print(f"Destination file is: '{Fore.GREEN + output_path + Fore.RESET}'")

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
    print("Original text     : " + Fore.YELLOW + original_text + Fore.RESET)
    (detected_lang, confidence) = detect_language(original_text)
    print(f"Detected lang     : {Fore.CYAN + str(detected_lang) + Fore.RESET}, confidence {Fore.CYAN + str(confidence) + Fore.RESET}")
    if detected_lang is None or confidence < 0.5:
        # print(f"Detected lang is not confident enough. Using supplied lang: {Fore.YELLOW + from_lang + Fore.RESET}")
        # detected_lang = from_lang
        print(Fore.RED + "Can't detect language. Skip this entry" + Fore.RESET)
        return

    if detected_lang == to_lang:
        print(Fore.GREEN + "Already translated to: " + to_lang + Fore.RESET)
        return

    # Find and replace dynamic placeholders ($$...$$) with unique tokens
    dynamic_placeholders = re.findall(r'\$\$.*?\$\$', original_text)
    for idx, placeholder in enumerate(dynamic_placeholders, start=1):
        token = f'PLACEHOLDER_DYNAMIC_{idx}'
        placeholder_mapping[placeholder] = token

    # Replace placeholders with tokens in the original text
    guarded_text = original_text
    for placeholder, token in placeholder_mapping.items():
        guarded_text = guarded_text.replace(placeholder, token)

    print("Guarded           : " + Fore.LIGHTBLUE_EX + guarded_text + Fore.RESET)

    # Translate the text with tokens
    # translated_text = translator.translate(guarded_text, src=detected_lang, dest=to_lang).text
    translated_text = translate_deepl(guarded_text, to_lang)
    print("Translated        : " + Fore.GREEN + translated_text + Fore.RESET)

    # Restore original placeholders in the translated text
    restored_text = translated_text
    for placeholder, token in placeholder_mapping.items():
        restored_text = restored_text.replace(token, placeholder)

    print("Unguarded         : " + Fore.CYAN + restored_text + Fore.RESET)
    text_elem.text = restored_text


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 5:
        print(f'Usage: {sys.argv[0]} <input_xml_path> <from_lang> <to_lang> <override y/n>'),
        sys.exit(1)

    input_path, from_lang, to_lang, override = sys.argv[1:5]
    translate_xml(input_path, from_lang, to_lang, override)
