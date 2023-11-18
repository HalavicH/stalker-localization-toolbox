import requests
from langdetect import LangDetectException

from sltools.commands.common import get_xml_files_and_log, process_files_with_progress
from sltools.utils.colorize import cf_blue
from sltools.utils.file_utils import read_xml, save_xml
from sltools.utils.misc import color_lang, detect_language
from sltools.utils.plain_text_utils import *
from sltools.utils.xml_utils import parse_xml_root, to_utf_string_with_proper_declaration, \
    format_xml_string
from sltools.utils.lang_utils import _tr


class AccessDeniedException(Exception):
    pass


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

    # TODO: handle errors
    log.debug(data)
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 403:
        raise AccessDeniedException()

    response_json = response.json()

    if response.status_code != 200:
        raise Exception(_tr('Error: %s') % response_json.get("message", _tr("API request failed")))

    translated_text = response_json['translations'][0]['text']
    guessed_language = response_json['translations'][0]['detected_source_language']
    if guessed_language is not None:
        log.debug(cf_blue(_tr("DeepL")) + _tr(" guessed lang: ") + guessed_language)

    return translated_text


def process_file(file_path, results: list, args):
    lang_to = args.to_lang
    lang_from = args.from_lang

    translated_text_block_cnt = []
    issues = []

    xml_string = read_xml(file_path)

    root = parse_xml_root(xml_string)

    try:
        for string_tag in root.findall('.//string'):
            process_string_translation(args, lang_from, lang_to, string_tag)
    except Exception:
        log.error(_tr("Fatal error during translation"))
        raise
    finally:
        translated_xml_str = to_utf_string_with_proper_declaration(root)
        formatted_xml_str = format_xml_string(translated_xml_str, file_path)
        save_xml(file_path, formatted_xml_str)

    results.append((file_path, translated_text_block_cnt, issues))


def process_string_translation(args, lang_from, lang_to, string_tag):
    string_id = string_tag.get('id')
    text_tag = string_tag.find('text')
    elem = text_tag
    if not elem.text or not elem.text.strip():
        log.info(_tr("Empty text block for string '%s'") % string_id)
        return
    orig_text = elem.text
    plain_text = purify_text(orig_text)
    try:
        lang, _ = detect_language(plain_text)
        if lang == lang_to:
            log.info(_tr("Text with id '%s' is already translated") % string_id)
            return
    except LangDetectException as e:
        log.warning(e)
        return
    # prepare text for translation
    replaced_text = replace_n_sym_with_newline(orig_text)
    color_guarded_text = guard_colors(replaced_text)
    color_and_pattern_guarded_text = guard_placeholders(color_guarded_text)
    prepared_text = color_and_pattern_guarded_text
    log.debug(_tr("Text prepared for translation"))
    log.always(_tr("Translating text with id '%s'") % string_id)
    try:
        # Translated the text fragment
        translated = translate_deepl(prepared_text, lang_to, args.api_key, lang_from)
    except AccessDeniedException as e:
        raise
    except Exception as e:
        log.error(_tr("Can't translate: '%s'. Error: %s" % (orig_text, e)))
        return

    # Restore translated text
    color_guarded_and_pattern_unguarded_text = unguard_placeholders(translated)
    unguarded_text = unguard_colors(color_guarded_and_pattern_unguarded_text)
    restored_text = replace_new_line_with_n_sym(unguarded_text)
    formatted_text = format_text_entry(restored_text, tabwidth * 3)
    # Replace text in file
    # elem.text = translated
    elem.text = formatted_text


def translate(args, is_read_only):
    action_msg = _tr("Translating from '%s' to '%s'") % (color_lang(args.from_lang), color_lang(args.to_lang))
    files = get_xml_files_and_log(args.paths, action_msg)
    results = []
    try:
        process_files_with_progress(files, process_file, results, args, is_read_only)
    except AccessDeniedException:
        log.error(_tr("Access forbidden. It seems that the token is invalid or expired"))
        return

    log.info(_tr("Total processed files: %d") % len(files))
    display_report(results)


def display_report(results):
    pass
