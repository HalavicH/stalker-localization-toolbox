#!/usr/bin/python3

"""
This script is All in one solution for working with localization of STALKER (X-ray 1.6.2+) games
It's capable of:
- fetching and validating localization text files
- analyzing and fixing encoding
- analyzing pattern misuse
- translating using DeepL
"""

import argparse
import os
import sys
import time
import traceback

from sltools.command_processor import process_command
from sltools.config import *
from sltools.utils.colorize import *
from sltools.log_config_loader import log
from sltools.utils.lang_utils import _tr

from rich_argparse import RichHelpFormatter

from sltools.utils.misc import check_for_update


def map_alias_to_command(args):
    for cmd in CMD_TO_ALIASES:
        if args.command in CMD_TO_ALIASES[cmd]:
            args.command = cmd


class CustomHelpFormatter(RichHelpFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, max_help_position=40, width=120)


class ExtendedHelpParser(argparse.ArgumentParser):
    def format_help(self):
        formatter = self._get_formatter()

        # usage
        formatter.add_usage(self.usage, self._actions,
                            self._mutually_exclusive_groups)

        # description
        formatter.add_text(self.description)

        # positionals, optionals and user-defined groups
        for action_group in self._action_groups:
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()

        # epilog
        formatter.add_text(self.epilog)

        # Add version check
        formatter.add_text(check_for_update())
        # determine help from format above
        return formatter.format_help()


def add_git_override_arguments(parser):
    parser.add_argument('--allow-no-repo', action='store_true', default=False,
                        help=_tr('Allow operations without Git repository'))
    parser.add_argument('--allow-dirty', action='store_true', default=False,
                        help=_tr('Allow operations on dirty Git repositories'))
    parser.add_argument('--allow-not-tracked', action='store_true', default=False,
                        help=_tr('Allow operations on untracked by Git files'))


def parse_args():
    parser = ExtendedHelpParser(description=_tr("app_description"), formatter_class=CustomHelpFormatter)
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.2')

    subparsers = parser.add_subparsers(dest='command', help=_tr('Sub-commands available:'))

    # validate-encoding | ve
    parser_ve = subparsers.add_parser(VALIDATE_ENCODING, aliases=CMD_TO_ALIASES[VALIDATE_ENCODING],
                                      formatter_class=parser.formatter_class,
                                      help=_tr('Validate encoding of a file or directory'))
    parser_ve.add_argument('paths', nargs='*', help=_tr('Paths to files or directories'))

    # fix-encoding | fe
    fe_help = _tr('Fix UTF-8 encoding of a file or directory (Warning: may break encoding if detected wrongly)')
    parser_fe = subparsers.add_parser(FIX_ENCODING, aliases=CMD_TO_ALIASES[FIX_ENCODING],
                                      formatter_class=parser.formatter_class, help=fe_help)
    parser_fe.add_argument('paths', nargs='*', help=_tr('Paths to files or directories'))
    add_git_override_arguments(parser_fe)

    # validate-xml | vx
    parser_vx = subparsers.add_parser(VALIDATE_XML, aliases=CMD_TO_ALIASES[VALIDATE_XML],
                                      formatter_class=parser.formatter_class,
                                      help=_tr('Validate XML of a file or directory'))
    parser_vx.add_argument('paths', nargs='*', help=_tr('Paths to files or directories'))

    # format-xml | fx
    parser_fx = subparsers.add_parser(FORMAT_XML, aliases=CMD_TO_ALIASES[FORMAT_XML],
                                      formatter_class=parser.formatter_class,
                                      help=_tr('Format XML of a file or directory'))
    parser_fx.add_argument('paths', nargs='*', help=_tr('Paths to files or directories'))
    parser_fx.add_argument('--fix', action='store_true',
                           help=_tr('Fix XML issues if possible instead of skipping the file'))
    parser_fx.add_argument('--format-text-entries', action='store_true',
                           help=_tr('Format <text> tag contents to resemble in-game appearance'))
    add_git_override_arguments(parser_fx)

    # check-primary-lang | cpl
    parser_cpl = subparsers.add_parser(CHECK_PRIMARY_LANG, aliases=CMD_TO_ALIASES[CHECK_PRIMARY_LANG],
                                       formatter_class=parser.formatter_class,
                                       help=_tr('Check primary language of a file or directory'))
    parser_cpl.add_argument('paths', nargs='*', help=_tr('Paths to files or directories'))
    cpl_help = _tr('Language to exclude from the report separated with "+". E.g: [cyan]--exclude uk+en[/cyan]')
    parser_cpl.add_argument('--exclude', dest='exclude', help=cpl_help)
    parser_cpl.add_argument('--detailed', action='store_true',
                            help=_tr('Show detailed report with language occurrences per file'))

    # translate | tr
    parser_tr = subparsers.add_parser(TRANSLATE, aliases=CMD_TO_ALIASES[TRANSLATE],
                                      formatter_class=parser.formatter_class,
                                      help=_tr('Translate text in a file or directory'))
    parser_tr.add_argument('paths', nargs='*', help=_tr('Paths to files or directories'))
    parser_tr.add_argument('--from', dest='from_lang', help=_tr('Source language (auto-detect if missing)'))
    parser_tr.add_argument('--to', dest='to_lang', required=True, help=_tr('Target language'))
    parser_tr.add_argument('--api-key', required=True, help=_tr('API key for translation service'))
    add_git_override_arguments(parser_tr)

    # analyze-patterns | ap
    parser_ap = subparsers.add_parser(ANALYZE_PATTERNS, aliases=CMD_TO_ALIASES[ANALYZE_PATTERNS],
                                      formatter_class=parser.formatter_class,
                                      help=_tr('Analyze patterns in a file or directory'))
    parser_ap.add_argument('paths', nargs='*', help=_tr('Paths to files or directories'))
    parser_ap.add_argument('--save', action='store_true', default=False,
                           help=_tr('Save detailed report as JSON file (for future comparison)'))
    # parser_ap.add_argument('--compare', dest='compare_to_path',
    #                        help='Compare freshly-generated analysis with one provided in file')

    # # fix-known-broken-patterns | fbp
    # parser_fbp = subparsers.add_parser(FIX_KNOWN_BROKEN_PATTERNS, aliases=CMD_TO_ALIASES[FIX_KNOWN_BROKEN_PATTERNS],
    #                                    formatter_class=parser.formatter_class,
    #                                    help='Fix known broken patterns in a file or directory')
    # parser_fbp.add_argument('paths', nargs='*', help=t('Paths to files or directories'))
    # add_git_override_arguments(parser_fbp)

    # capitalize-text | ct
    ct_help = _tr('Capitalize first letter [cyan](a->A)[/cyan] in all text entries in a file or directory')
    parser_ct = subparsers.add_parser(CAPITALIZE_TEXT, aliases=CMD_TO_ALIASES[CAPITALIZE_TEXT],
                                      formatter_class=parser.formatter_class, help=ct_help)
    parser_ct.add_argument('paths', nargs='*', help='Paths to files or directories')
    add_git_override_arguments(parser_ct)

    # find-string-dups | fsd
    fsd_help = _tr("Looks for duplicates of [green]'<string id=\"...\">'[/green] to eliminate unwanted conflicts/overrides. Provides filecentric report by default")
    parser_fsd = subparsers.add_parser(FIND_STRING_DUPLICATES, aliases=CMD_TO_ALIASES[FIND_STRING_DUPLICATES],
                                       formatter_class=parser.formatter_class, help=fsd_help)
    parser_fsd.add_argument('--per-string-report', action='store_true', default=False,
                            help=_tr('Display detailed report with string text'))
    parser_fsd.add_argument('--web-visualizer', action='store_true', default=False,
                            help=_tr('Display duplicates as D3 interactive graph'))
    parser_fsd.add_argument('--save-report', action='store_true', default=False,
                            help=_tr('Save filecentric report as JSON'))
    parser_fsd.add_argument('paths', nargs='*', help='Paths to files or directories')

    # find-string-dups | fsd
    parser_sfwd = subparsers.add_parser(SORT_FILES_WITH_DUPLICATES, aliases=CMD_TO_ALIASES[SORT_FILES_WITH_DUPLICATES],
                                        formatter_class=parser.formatter_class,
                                        help=_tr("Sorts strings in files alphabetically placing duplicates on top"))
    parser_sfwd.add_argument('--sort-duplicates-only', action='store_true', default=False,
                             help=_tr("Don't sort non-duplicates"))
    parser_sfwd.add_argument('paths', nargs='*',
                             help=_tr('Paths to two files you want to compare and sort dups'))
    add_git_override_arguments(parser_sfwd)

    ###### Parse ######
    args = parser.parse_args()
    log.debug(f"Args: {args}")

    map_alias_to_command(args)

    if args.command is None:
        cmd_name = sys.argv[0].split("/")[-1] + " -h"
        log.always(_tr(f"Please provide args. Use {cf_green(cmd_name)} for help"))
        sys.exit()

    return args


def main():
    start_time = time.process_time()

    try:
        log.debug(_tr("Start"))
        args: argparse.Namespace = parse_args()

        # testing(args)
        process_command(args)
    except Exception as e:
        if os.environ.get("PY_ST"):
            log.fatal(_tr("Failed to perform actions. Error: %s") % traceback.format_exc())
        else:
            log.fatal(_tr("Failed to perform actions. Error: %s") % e)

    end_time = time.process_time()
    elapsed_time = end_time - start_time
    log.always(_tr("Done! Total time: %s") % cf_green("%.3fs" % elapsed_time))
    get_console().print(check_for_update())


def testing(args):
    log.debug(f"Args: {args}")
    log.info(f"Args: {args}")
    log.warning(f"Args: {args}")
    log.error(f"Args: {args}")
    log.critical(f"Args: {args}")
    log.info(
        cf_black("black") +
        cf_red("red") +
        cf_green("green") +
        cf_yellow("yellow") +
        cf_blue("blue") +
        cf_magenta("magenta") +
        cf_cyan("cyan") +
        cf_white("white") +
        cb_black("black") +
        cb_red("red") +
        cb_green("green") +
        cb_yellow("yellow") +
        cb_blue("blue") +
        cb_magenta("magenta") +
        cb_cyan("cyan") +
        cb_white("white")
    )


if __name__ == '__main__':
    main()
