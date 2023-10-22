import requests
from langdetect import LangDetectException

from src.commands.common import get_xml_files_and_log, process_files_with_progress
from src.log_config_loader import log
from src.utils.colorize import cf_blue
from src.utils.file_utils import read_xml, save_xml
from src.utils.lang_utils import detect_language
from src.utils.misc import color_lang
from src.utils.plain_text_utils import *
from src.utils.xml_utils import extract_text_from_xml, parse_xml_root, to_utf_string_with_proper_declaration, \
    format_xml_string


def translate_deepl(text, target_language, api_key, src_language=None):
    url = 'https://api-free.deepl.com/v2/translate'
    headers = {
        'Authorization': f'DeepL-Auth-Key {api_key}'
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
        log.debug(cf_blue("DeepL") + " guessed lang: " + guessed_language)

    return translated_text


def process_file(file_path, results: list, args):
    lang_to = args.to_lang

    translated_text_block_cnt = []
    issues = []

    xml_string = read_xml(file_path)

    root = parse_xml_root(xml_string)
    for elem in root.xpath('//text'):
        if not elem.text or not elem.text.strip():
            log.debug("Empty text block")
            continue

        orig_text = elem.text
        # prepare text for translation
        replaced_text = replace_n_sym_with_newline(orig_text)
        color_guarded_text = guard_colors(replaced_text)
        color_and_pattern_guarded_text = guard_placeholders(color_guarded_text)
        prepared_text = color_and_pattern_guarded_text
        log.debug("Text prepared for translation")

        # Translated the text fragment
        translated = translate_deepl(prepared_text, lang_to, args.api_key)

        # Restore translated text
        color_guarded_and_pattern_unguarded_text = unguard_placeholders(translated)
        unguarded_text = unguard_colors(color_guarded_and_pattern_unguarded_text)
        restored_text = replace_new_line_with_n_sym(unguarded_text)
        formatted_text = format_text_entry(restored_text, tabwidth * 3)

        # Replace text in file
        # elem.text = translated
        elem.text = formatted_text

    translated_xml_str = to_utf_string_with_proper_declaration(root)
    formatted_xml_str = format_xml_string(translated_xml_str, file_path)
    save_xml(file_path, formatted_xml_str)

    results.append((file_path, translated_text_block_cnt, issues))


def translate(args):
    action_msg = f"Translating from '{color_lang(args.from_lang)}' to '{color_lang(args.to_lang)}'"
    files = get_xml_files_and_log(args.paths, action_msg)
    results = []
    process_files_with_progress(files, process_file, results, args)
    log.info(f"Total processed files: {len(files)}")
    display_report(results)


def display_report(results):
    pass
