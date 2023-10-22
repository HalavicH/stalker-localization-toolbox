from langdetect import LangDetectException

from src.commands.common import process_files_with_progress, get_xml_files_and_log
from src.log_config_loader import log
from src.utils.colorize import *
from src.utils.file_utils import read_xml
from src.utils.lang_utils import detect_language
from src.utils.misc import create_pretty_table, color_lang
from src.utils.xml_utils import parse_xml_root, extract_text_from_xml


def process_file(file_path, results: list, args):
    detailed = args.detailed or False
    stats = {
        "Unknown": 0
    }
    xml_string = read_xml(file_path)

    root = parse_xml_root(xml_string)
    texts = [elem.text for elem in root.xpath('//text') if elem.text and elem.text.strip()]

    if detailed:
        for text in texts:
            try:
                language, probability = detect_language(text)
            except LangDetectException as e:
                log.debug(e, text)
                stats["Unknown"] += 1
                continue

            if stats.get(language) is None:
                stats[language] = 1
            else:
                stats[language] += 1

    all_text = extract_text_from_xml(xml_string)
    try:
        main_lang, _ = detect_language(all_text)
    except LangDetectException as e:
        log.debug("Can't detect language for the whole file. Probably it's empty")
        main_lang = "Unknown"

    results.append((file_path, stats, main_lang))


def check_primary_lang(args):
    files = get_xml_files_and_log(args.path, "Analyzing primary language for")
    results = []
    process_files_with_progress(files, process_file, results, args)
    log.info(f"Total processed files: {len(files)}")
    display_report(results)


def display_report(report, detailed=False):
    if len(report) == 0:
        log.info(cf_green("No files with bad encoding detected!"))
        return

    report = sorted(report, key=lambda tup: tup[2])

    table_title = cf_yellow(f"Short report on language (total: {len(report)})")
    column_names = ["Filename", "Main Lang"]
    table = create_pretty_table(column_names)

    for filename, _, lang in report:
        lang = color_lang(lang)
        table.add_row([filename, lang])

    log.always(table_title + "\n" + str(table))  # PrettyTable objects can be converted to string using str()

    if detailed:
        display_detailed_report(report)


def display_detailed_report(report):
    table_title = cf_red(f"Detailed report on language (total: {len(report)})")
    column_names = ["Filename", "Language", "Count"]
    table = create_pretty_table(column_names)
    longest = 0
    for filename, stats in report:
        if len(filename) > longest:
            longest = len(filename)
    for filename, stats in report:
        table.add_row(["─" * longest, "─" * len("Language"), "─" * len("Count")])
        table.add_row([cf_cyan(filename), cf_cyan("Language"), cf_cyan("Count")])
        sorted_keys = sorted(stats.keys())

        for lang in sorted_keys:
            stats_num = stats[lang]
            if lang == "Unknown":
                lang = cf_red(lang)

            table.add_row(["", lang, stats_num])
    log.always(table_title + "\n" + str(table))  # PrettyTable objects can be converted to string using str()
