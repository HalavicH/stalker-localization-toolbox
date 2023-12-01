import os

from rich import get_console

from sltools.baseline.command_baseline import AbstractCommand
from sltools.baseline.common import get_xml_files_and_log
from sltools.log_config_loader import log
from sltools.utils.colorize import cf_cyan, cf_yellow, cf_green
from sltools.utils.file_utils import read_xml, save_xml
from sltools.utils.lang_utils import trn
from sltools.utils.misc import create_table
from sltools.utils.xml_utils import format_xml_string, parse_xml_root, to_utf_string_with_proper_declaration


class CompareTextLocalizations(AbstractCommand):
    # Metadata
    ##########
    def get_name(self) -> str:
        return "compare-text-localizations"

    def get_aliases(self) -> list:
        return ['ctl']

    def _get_help(self) -> str:
        return trn('(WebUI) Compare strings two text localizations by ids and content')

    def _setup_parser_args(self, parser):
        parser.add_argument('paths', nargs='*', help=trn('Paths to two localization directories. E.g eng ukr'))

    # Execution
    ###########
    def _process_file(self, file_path, results: dict, args):
        pass

    @staticmethod
    def compare_locales(locale1_files, locale2_files):
        same_filenames = set(locale1_files).intersection(locale2_files)
        extra_filenames_locale1 = set(locale1_files) - set(locale2_files)
        extra_filenames_locale2 = set(locale2_files) - set(locale1_files)

        return {
            "same-filenames": list(same_filenames),
            "unique-filenames-locale1": list(extra_filenames_locale1),
            "unique-filenames-locale2": list(extra_filenames_locale2)
        }

    @staticmethod
    def get_locale_info(locale_path):
        locale_name = os.path.basename(os.path.normpath(locale_path))
        filenames = [f for f in os.listdir(locale_path) if os.path.isfile(os.path.join(locale_path, f))]
        return locale_name, filenames

    @staticmethod
    def validate_path(path):
        return os.path.isdir(path)

    def execute(self, args) -> dict:
        if len(args.paths) != 2:
            log.error("Command requires two valid paths to localizations!")
            return {}

        locale1_name, locale1_files = self.get_locale_info(args.paths[0])
        locale2_name, locale2_files = self.get_locale_info(args.paths[1])

        comparison_results = self.compare_locales(locale1_files, locale2_files)

        results = {
            "file_report": {
                "locale1": {
                    "name": locale1_name,
                    "file-cnt": len(locale1_files),
                    "unique-filenames-cnt": len(comparison_results["unique-filenames-locale1"]),
                    "unique-filenames": comparison_results["unique-filenames-locale1"]
                },
                "locale2": {
                    "name": locale2_name,
                    "file-cnt": len(locale2_files),
                    "unique-filenames-cnt": len(comparison_results["unique-filenames-locale2"]),
                    "unique-filenames": comparison_results["unique-filenames-locale2"]
                },
                "same-filenames": comparison_results["same-filenames"]
            }
        }

        return results

    # Displaying
    ############
    def display_result(self, result: dict):
        if not result or 'file_report' not in result:
            log.always("No report data available.")
            return

        file_report = result['file_report']

        for locale_key in ['locale1', 'locale2']:
            data = file_report[locale_key]
            log.always("Locale '%s' Report:" % data['name'])
            log.always("  Total Files: %s" % data['file-cnt'])
            log.always("  Unique Filenames Count: %s" % data['unique-filenames-cnt'])
            if data['unique-filenames-cnt'] > 0:
                log.always(cf_cyan("  Unique Filenames:"))
                for filename in data['unique-filenames']:
                    log.always(cf_cyan("    - %s" % filename))

        log.always(cf_green("Same Filenames Across Locales (%s files):" % len(file_report['same-filenames'])))
        for filename in file_report['same-filenames']:
            log.always(cf_green("    - %s" % filename))

        log.always("")  # For an empty line between sections
