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

from src.command_processor import process_command
from src.config import *
from src.utils.colorize import *
from src.log_config_loader import log

from rich_argparse import RichHelpFormatter


def map_alias_to_command(args):
    for cmd in CMD_TO_ALIASES:
        if args.command in CMD_TO_ALIASES[cmd]:
            args.command = cmd


class CustomHelpFormatter(RichHelpFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, max_help_position=40, width=120)

    def _format_action(self, action):
        # Customize the formatting of action here if needed
        return super()._format_action(action)


def parse_args():
    parser = argparse.ArgumentParser(description='My App Description', formatter_class=CustomHelpFormatter)

    subparsers = parser.add_subparsers(dest='command', help='Sub-commands available:')

    # validate-encoding | ve
    parser_ve = subparsers.add_parser(VALIDATE_ENCODING, aliases=CMD_TO_ALIASES[VALIDATE_ENCODING],
                                      formatter_class=parser.formatter_class,
                                      help='Validate encoding of a file or directory')
    parser_ve.add_argument('paths', nargs='*', help='Paths to files or directories')

    # fix-encoding | fe
    parser_fe = subparsers.add_parser(FIX_ENCODING, aliases=CMD_TO_ALIASES[FIX_ENCODING],
                                      formatter_class=parser.formatter_class,
                                      help='Fix UTF-8 encoding of a file or directory (Warning: may break encoding if detected wrongly)')
    parser_fe.add_argument('paths', nargs='*', help='Paths to files or directories')

    # validate-xml | vx
    parser_vx = subparsers.add_parser(VALIDATE_XML, aliases=CMD_TO_ALIASES[VALIDATE_XML],
                                      formatter_class=parser.formatter_class,
                                      help='Validate XML of a file or directory')
    parser_vx.add_argument('paths', nargs='*', help='Paths to files or directories')

    # format-xml | fx
    parser_fx = subparsers.add_parser(FORMAT_XML, aliases=CMD_TO_ALIASES[FORMAT_XML],
                                      formatter_class=parser.formatter_class,
                                      help='Format XML of a file or directory')
    parser_fx.add_argument('--fix', action='store_true', help='Fix XML issues if possible instead of skipping the file')
    parser_fx.add_argument('--format-text-entries', action='store_true',
                           help='Format <text> tag contents to resemble in-game appearance')

    parser_fx.add_argument('paths', nargs='*', help='Paths to files or directories')

    # check-primary-lang | cpl
    parser_cpl = subparsers.add_parser(CHECK_PRIMARY_LANG, aliases=CMD_TO_ALIASES[CHECK_PRIMARY_LANG],
                                       formatter_class=parser.formatter_class,
                                       help='Check primary language of a file or directory')
    parser_cpl.add_argument('paths', nargs='*', help='Paths to files or directories')
    parser_cpl.add_argument('--exclude', dest='exclude',
                            help='Language to exclude from the report separated with "+". E.g: ' + cf_cyan("--exclude uk+en"))
    parser_cpl.add_argument('--detailed', action='store_true',
                            help='Show detailed report with language occurrences per file')

    # translate | tr
    parser_tr = subparsers.add_parser(TRANSLATE, aliases=CMD_TO_ALIASES[TRANSLATE],
                                      formatter_class=parser.formatter_class,
                                      help='Translate text in a file or directory')
    parser_tr.add_argument('paths', nargs='*', help='Paths to files or directories')
    parser_tr.add_argument('--from', dest='from_lang', help='Source language (auto-detect if missing)')
    parser_tr.add_argument('--to', dest='to_lang', required=True, help='Target language')
    parser_tr.add_argument('--api-key', required=True, help='API key for translation service')

    # analyze-patterns | ap
    parser_ap = subparsers.add_parser(ANALYZE_PATTERNS, aliases=CMD_TO_ALIASES[ANALYZE_PATTERNS],
                                      formatter_class=parser.formatter_class,
                                      help='Analyze patterns in a file or directory')
    parser_ap.add_argument('paths', nargs='*', help='Paths to files or directories')

    # fix-known-broken-patterns | fbp
    parser_fbp = subparsers.add_parser(FIX_KNOWN_BROKEN_PATTERNS, aliases=CMD_TO_ALIASES[FIX_KNOWN_BROKEN_PATTERNS],
                                       formatter_class=parser.formatter_class,
                                       help='Fix known broken patterns in a file or directory')
    parser_fbp.add_argument('paths', nargs='*', help='Paths to files or directories')

    # TODO: Change log level with env variable
    # # Global logging level settings
    # log_group = parser.add_mutually_exclusive_group()
    # log_group.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    #                        help='Set log level')
    # log_group.add_argument('--verbose', action='store_true', help='Set log level to DEBUG')

    args = parser.parse_args()
    log.debug(f"Args: {args}")

    map_alias_to_command(args)

    if args.command is None:
        cmd_name = sys.argv[0].split("/")[-1] + " -h"
        log.always(f"Please provide args. Use {cf_green(cmd_name)} for help")
        sys.exit()

    return args


def main():
    start_time = time.process_time()

    try:
        log.debug("Start")
        args: argparse.Namespace = parse_args()

        # testing(args)
        process_command(args)
    except Exception as e:
        if os.environ.get("PY_ST"):
            log.fatal(f"Failed to perform actions. Error: {traceback.format_exc()}")
        else:
            log.fatal(f"Failed to perform actions. Error: {e}")

    end_time = time.process_time()
    elapsed_time = end_time - start_time
    log.always("Done! Total time: %s" % cf_green("%.3fs" % elapsed_time))


def testing(args):
    log.debug(f"Args: {args}")
    log.info(f"Args: {args}")
    log.warning(f"Args: {args}")
    log.error(f"Args: {args}")
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
