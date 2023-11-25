from langdetect import LangDetectException

from sltools.commands.utils.common import process_files_with_progress, get_xml_files_and_log
from sltools.config import UNKNOWN_LANG, TOO_LITTLE_DATA, min_recognizable_text_length
from sltools.utils.colorize import *
from sltools.utils.error_utils import interpret_error
from sltools.utils.file_utils import read_xml
from sltools.utils.misc import create_table, color_lang, detect_language
from sltools.utils.plain_text_utils import *
from sltools.utils.xml_utils import parse_xml_root, extract_text_from_xml
from sltools.utils.lang_utils import trn


def process_file(file_path, results: list, args):
    exclude_langs = args.exclude_langs
    detailed = args.detailed or False
    stats = {UNKNOWN_LANG: 0, TOO_LITTLE_DATA: 0}
    xml_string = read_xml(file_path)

    root = parse_xml_root(xml_string)
    texts = [elem.text for elem in root.xpath('//text') if elem.text and elem.text.strip()]

    if detailed:
        for text in texts:
            text = purify_text(text)
            try:
                language, probability = detect_language(text)
                if len(text) < min_recognizable_text_length:
                    language = TOO_LITTLE_DATA
            except LangDetectException as e:
                log.debug(interpret_error(e), text)
                stats[TOO_LITTLE_DATA] += 1
                continue

            if language in exclude_langs:
                log.debug(trn("Lang %s is in excludes. Skipping") % language)
                continue

            stats[language] = stats.get(language, 0) + 1

    all_text = extract_text_from_xml(xml_string)
    all_text = purify_text(all_text)
    try:
        main_lang, _ = detect_language(all_text)
        if main_lang in exclude_langs:
            main_lang = None
        if len(all_text) < min_recognizable_text_length:
            main_lang = TOO_LITTLE_DATA
    except LangDetectException as e:
        log.debug(interpret_error(e))
        log.info(trn("Can't detect language for the whole file. Probably it's empty"))
        main_lang = TOO_LITTLE_DATA

    results.append((file_path, stats, main_lang))


def check_primary_lang(args, is_read_only):
    exclude_langs = (args.exclude or "").split("+")
    args.exclude_langs = exclude_langs
    files = get_xml_files_and_log(args.paths, trn("Analyzing primary language for"))
    results = []
    process_files_with_progress(files, process_file, results, args, is_read_only)
    log.info(trn("Total processed files: %s") % len(files))
    display_report(results, args.detailed)


def display_report(report, detailed):
    if len(report) == 0:
        log.info(cf_green(trn("No files detected!. Nothing to show")))
        return

    report = list(filter(lambda tup: tup[2] is not None, report))
    report = sorted(report, key=lambda tup: tup[2])

    table_title = cf_cyan(trn("Short report on language. Total: %s files") % len(report))
    column_names = [trn("Filename"), trn("Main Lang")]
    table = create_table(column_names)

    for filename, _, lang in report:
        if lang is None:
            continue

        lang = color_lang(lang)
        table.add_row(filename, lang)

    log.always(table_title)
    get_console().print(table)

    if detailed:
        display_detailed_report(report)


def display_detailed_report(report):
    table_title = cf_cyan(trn("Detailed report (per each string). Total: %s files") % len(report))
    column_names = [trn("Filename"), trn("Language"), trn("Count")]
    table = create_table(column_names)
    longest = max(len(filename) for filename, _, _ in report)

    for filename, stats, _ in report:
        table.add_row("─" * longest, "─" * len(trn("Too little data")), "─" * len(trn("Count")))
        table.add_row(cf_cyan(filename), cf_cyan(trn("Language")), cf_cyan(trn("Count")))
        sorted_keys = sorted(stats.keys())

        for lang in sorted_keys:
            stats_num = stats[lang]
            if stats_num == 0:
                continue
            if lang == "Unknown":
                lang = cf_red(lang)

            table.add_row("", color_lang(lang), str(stats_num))

    log.always(table_title)
    get_console().print(table)
