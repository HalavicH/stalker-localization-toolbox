import requests
from googletrans import Translator
from langdetect import LangDetectException
from rich import get_console

from sltools.baseline.command_baseline import AbstractCommand
from sltools.log_config_loader import log
from sltools.old.commands.format_xml import error_str, format_xml_text_entries, to_yes_no
from sltools.old.commands.utils.common import get_xml_files_and_log, process_files_with_progress
from sltools.utils.colorize import cf_green, cf_red, cf_yellow, cf_cyan, cf_blue
from sltools.utils.error_utils import log_and_save_error, interpret_error
from sltools.utils.file_utils import read_xml, save_xml
from sltools.utils.lang_utils import trn
from sltools.utils.misc import create_table, exception_originates_from, color_lang, detect_language
from sltools.utils.plain_text_utils import tabwidth, format_text_entry, unguard_placeholders, unguard_colors, replace_new_line_with_n_sym, \
    replace_n_sym_with_newline, guard_colors, guard_placeholders, purify_text
from sltools.utils.xml_utils import fix_possible_errors, format_xml_string, parse_xml_root, indent, to_utf_string_with_proper_declaration, \
    add_blank_line_before_comments


class AccessDeniedException(Exception):
    pass


translator = Translator()


def translate_google(text, target_language, src_language):
    if src_language:
        return translator.translate(text, src=src_language, dest=target_language).text
    else:
        return translator.translate(text, dest=target_language).text


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
        raise Exception('%s' % response_json.get("message", trn("API request failed")))

    translated_text = response_json['translations'][0]['text']
    guessed_language = response_json['translations'][0]['detected_source_language']
    if guessed_language is not None:
        log.debug(cf_blue(trn("DeepL")) + trn(" guessed lang: ") + guessed_language)

    return translated_text


def process_string_translation(args, lang_from, lang_to, string_tag):
    string_id = string_tag.get('id')
    text_tag = string_tag.find('text')
    elem = text_tag
    if not elem.text or not elem.text.strip():
        log.info(trn("Empty text block for string '%s'") % string_id)
        return
    orig_text = elem.text
    plain_text = purify_text(orig_text)
    try:
        lang, _ = detect_language(plain_text)
        if lang == lang_to:
            log.info(trn("Text with id '%s' is already translated") % string_id)
            return
    except LangDetectException as e:
        log.warning(interpret_error(e))
        return
    # prepare text for translation
    replaced_text = replace_n_sym_with_newline(orig_text)
    color_guarded_text = guard_colors(replaced_text)
    color_and_pattern_guarded_text = guard_placeholders(color_guarded_text)
    prepared_text = color_and_pattern_guarded_text
    log.debug(trn("Text prepared for translation"))
    log.always(trn("Translating text with id '%s'") % string_id)
    try:
        # Translated the text fragment
        if args.api_key:
            translated = translate_deepl(prepared_text, lang_to, args.api_key, lang_from)
        else:
            translated = translate_google(prepared_text, lang_to, lang_from)
    except AccessDeniedException:
        raise
    # except TooManyRequestsException as e:
    #     raise Exception
    except Exception as e:
        log.error(trn("Can't translate: '%s'. Error: %s" % (orig_text, interpret_error(e))))
        return

    # Restore translated text
    color_guarded_and_pattern_unguarded_text = unguard_placeholders(translated)
    unguarded_text = unguard_colors(color_guarded_and_pattern_unguarded_text)
    restored_text = replace_new_line_with_n_sym(unguarded_text)
    formatted_text = format_text_entry(restored_text, tabwidth * 3)
    # Replace text in file
    # elem.text = translated
    elem.text = formatted_text


class Translate(AbstractCommand):
    # Metadata
    ##########
    def get_name(self) -> str:
        return "translate"

    def get_aliases(self) -> list:
        return ['tr']

    def _get_help(self) -> str:
        return trn('Translate text in a file or directory')

    def _setup_parser_args(self, parser):
        parser.add_argument('paths', nargs='*', help=trn('Paths to files or directories'))
        parser.add_argument('--from', dest='from_lang', help=trn('Source language (auto-detect if missing)'))
        parser.add_argument('--to', dest='to_lang', required=True, help=trn('Target language'))
        parser.add_argument('--api-key', help=trn("API key for translation service. If absent Google Translation be used (it sucks)"))
        self._add_git_override_arguments(parser)

    # Execution
    ###########
    def _process_file(self, file_path, results: dict, args):
        report = results["report"]
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
            log.error(trn("Fatal error during translation"))
            raise
        finally:
            translated_xml_str = to_utf_string_with_proper_declaration(root)
            formatted_xml_str = format_xml_string(translated_xml_str, file_path)
            save_xml(file_path, formatted_xml_str)

        report.append((file_path, translated_text_block_cnt, issues))

    def execute(self, args) -> dict:
        action_msg = trn("Translating from '%s' to '%s'") % (color_lang(args.from_lang), color_lang(args.to_lang))
        files = get_xml_files_and_log(args.paths, action_msg)

        results = {"report": []}
        try:
            self.process_files_with_progressbar(args, files, results, False)
        except AccessDeniedException:
            log.error(trn("Access forbidden. It seems that the token is invalid or expired"))
            return {}

        return results

    # Displaying
    ############
    def display_result(self, result: dict):
        pass
