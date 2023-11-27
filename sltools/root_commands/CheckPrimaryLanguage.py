from langdetect import LangDetectException
from rich import get_console

from sltools.baseline.command_baseline import AbstractCommand
from sltools.log_config_loader import log
from sltools.old.commands.utils.common import get_xml_files_and_log
from sltools.old.config import UNKNOWN_LANG, TOO_LITTLE_DATA, min_recognizable_text_length
from sltools.utils.colorize import cf_green, cf_red, cf_cyan
from sltools.utils.error_utils import interpret_error
from sltools.utils.file_utils import read_xml
from sltools.utils.lang_utils import trn
from sltools.utils.misc import create_table, detect_language, color_lang
from sltools.utils.plain_text_utils import purify_text
from sltools.utils.xml_utils import parse_xml_root, extract_text_from_xml


class CheckPrimaryLanguage(AbstractCommand):
    # Metadata
    ##########
    def get_name(self) -> str:
        return "check-primary-lang"

    def get_aliases(self) -> list:
        return ['cpl']

    def _get_help(self) -> str:
        return trn('Check primary language of a file or directory')

    def _setup_parser_args(self, parser):
        parser.add_argument('paths', nargs='*', help=trn('Paths to files or directories'))
        cpl_help = trn('Language to exclude from the report separated with "+". E.g: [cyan]--exclude uk+en[/cyan]')
        parser.add_argument('--exclude', dest='exclude', help=cpl_help)
        parser.add_argument('--detailed', action='store_true',
                            help=trn('Show detailed report with language occurrences per file'))

    # Execution
    ###########
    def _process_file(self, file_path, results: dict, args):
        report = results["report"]
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

        report.append((file_path, stats, main_lang))

    def execute(self, args) -> dict:
        exclude_langs = (args.exclude or "").split("+")
        args.exclude_langs = exclude_langs
        files = get_xml_files_and_log(args.paths, trn("Analyzing primary language for"))
        results = {"report": [], "detailed": args.detailed}
        self.process_files_with_progressbar(args, files, results, True)
        log.info(trn("Total processed files: %s") % len(files))

        return results

    # Displaying
    ############
    def display_result(self, result: dict):
        report: list = result["report"]
        detailed: list = result["detailed"]
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
            self.display_detailed_report(report)

    @staticmethod
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
