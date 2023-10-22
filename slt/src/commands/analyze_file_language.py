import rich
from langdetect import LangDetectException

from src.log_config_loader import log

import time

from rich.progress import Progress

from prettytable import PrettyTable

from src.log_config_loader import log
from src.utils.colorize import *
from src.utils.encoding_utils import detect_encoding, is_file_content_win1251_compatible
from src.utils.file_utils import find_xml_files, read_xml
from src.utils.lang_utils import detect_language
from src.utils.misc import get_term_width, create_pretty_table
from src.utils.xml_utils import parse_xml_root, extract_text_from_xml


def process_file(file_path, results: list, detailed=False):
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


def color_lang(lang):
    lang_to_colored = {
        "uk": cf_green("uk"),
        "ru": cf_red("ru"),
        "en": cf_blue("en"),
        "pl": cf_cyan("pl"),
        "fr": cf_yellow("fr"),
        "sp": cf_magenta("sp"),
        "Unknown": cf_red("Unknown"),
    }

    colored = lang_to_colored.get(lang)
    if colored is None:
        colored = cf_red("Unknown2")
    return colored


def print_report(report, detailed=False):
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


def check_primary_lang(args):
    files = find_xml_files(args.path)
    log.always(f"Alanyzing primary language {cf_green(len(files))} files")

    term_width = get_term_width()
    if term_width > 130:
        max_file_width = term_width - 80
    else:
        max_file_width = term_width - 60

    results = []
    with Progress() as progress:
        task = progress.add_task("", total=len(files))
        for i, file in enumerate(files):
            # Truncate the file path if it exceeds the maximum width
            truncated_file = (
                "..." + file[-(max_file_width - 5):]
                if len(file) > max_file_width
                else file.ljust(max_file_width)
            )

            # Update the progress bar with the truncated description
            progress.update(task, completed=i,
                            description=f"Processing file [green]#{i:03}[/] with name [green]{truncated_file}[/]")

            log.debug(f"Processing file #{i}")
            process_file(file, results)

    log.info(f"Total processed files: {len(files)}")

    print_report(results)
