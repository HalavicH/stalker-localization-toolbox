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
from importlib.metadata import version

from rich_argparse import RichHelpFormatter

from sltools.baseline.command_processor import CommandProcessor
from sltools.baseline.parser_definitions import ExtendedHelpParser, BooleanAction, add_git_override_arguments, CustomHelpFormatter
from sltools.old.command_processor import process_command
from sltools.old.config import *
from sltools.config_file_manager import ConfigFileManager, file_config
from sltools.log_config_loader import log
from sltools.root_commands.AnalyzePatterns import AnalyzePatterns
from sltools.root_commands.CapitalizeText import CapitalizeText
from sltools.root_commands.CheckPrimaryLanguage import CheckPrimaryLanguage
from sltools.root_commands.Config import Config
from sltools.root_commands.FindStringDuplicates import FindStringDuplicates
from sltools.root_commands.FixEncoding import FixEncoding
from sltools.root_commands.FormatXml import FormatXml
from sltools.root_commands.Misc import Misc
from sltools.root_commands.SortFilesWithDuplicates import SortFilesWithDuplicates
from sltools.root_commands.Translate import Translate
from sltools.root_commands.ValidateEncoding import ValidateEncoding
from sltools.root_commands.ValidateXml import ValidateXml
from sltools.utils.colorize import *
from sltools.utils.lang_utils import trn
from sltools.utils.misc import check_for_update, check_deepl_tokens_usage


def parse_args():
    parser = ExtendedHelpParser(description=trn("app_description"), formatter_class=CustomHelpFormatter)
    parser.add_argument('--version', action='version', version=version('sltools'))

    subparsers = parser.add_subparsers(dest='command', help=trn('Sub-commands available:'))

    init_text_actions_parser(parser.formatter_class, subparsers)
    init_mo2_actions_subparser(parser.formatter_class, subparsers)

    # Add misc subparser
    parser_misc = subparsers.add_parser('misc',
                                        formatter_class=parser.formatter_class,
                                        help=trn('Misc housekeeping and experimental commands'))
    parser_misc.add_argument('--check-deepl-tokens-usage',
                             nargs='+',  # '+' means "at least one"
                             help=trn('Checks DeepL tokens quota (provide token list separated by the space'))

    ###### Parse ######
    args = parser.parse_args()
    log.debug(f"Args: {args}")

    if args.command is None:
        cmd_name = sys.argv[0].split("/")[-1] + " -h"
        log.always(trn(f"Please provide args. Use {cf_green(cmd_name)} for help"))
        sys.exit()

    return args


def init_mo2_actions_subparser(formatter_class, subparsers):
    # Add MO2 subparser
    mo2_subparsers = subparsers.add_parser('mo2',
                                           formatter_class=formatter_class,
                                           help=trn('Commands for managing and processing Mod Organizer 2 (MO2) mods'))
    mo2_subparsers = mo2_subparsers.add_subparsers(dest='subcommand', help=trn('Sub-commands available:'))

    # Add VFS mapping subparser
    vfs_map_parser = mo2_subparsers.add_parser(VFS_MAP, aliases=MO2_CMD_TO_ALIASES[VFS_MAP],
                                               formatter_class=formatter_class,
                                               help=trn('Map VFS file tree to physical file paths for MO2 mods'))
    vfs_map_parser.add_argument('--vfs-file', required=True, dest="vfs_file",
                                help=trn('Path to the VFS file tree report from MO2'))
    vfs_map_parser.add_argument('--output-file', required=True, dest="output_file",
                                help=trn('File to output the mapped physical file paths to'))
    vfs_map_parser.add_argument('--merge', action='store_true',
                                help=trn('Combine all mod files into a single directory, mimicking the VFS structure.'))
    vfs_map_parser.add_argument('--exclude-patterns', dest='exclude_patterns',
                                help=trn('Exclude files or mods matching these patterns (separate multiple patterns with "|")'))
    vfs_map_parser.add_argument('--include-patterns', dest='include_patterns',
                                help=trn('Include only files or mods matching these patterns (separate multiple patterns with "|")'))

    # Add VFS copy subparser
    vfs_copy_parser = mo2_subparsers.add_parser(VFS_COPY, aliases=MO2_CMD_TO_ALIASES[VFS_COPY],
                                                formatter_class=formatter_class,
                                                help=trn('Create a physical copy of the MO2 VFS using a list of real file paths'))

    # Arguments for vfs-copy command
    vfs_copy_parser.add_argument('--real-paths-file', required=True, dest="real_paths_file",
                                 help=trn('Path to the file containing real paths of the VFS (output from vfs-map command)'))
    vfs_copy_parser.add_argument('--mo2-base-dir', required=True, dest="mo2_base_dir",
                                 help=trn('Path to the base directory of Mod Organizer 2'))
    vfs_copy_parser.add_argument('--output-dir', required=True, dest="output_dir",
                                 help=trn('Directory where the physical copy of the VFS will be created'))
    # Create a mutually exclusive group for the mode of operation
    mode_group = vfs_copy_parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--merge', action='store_true',
                            help=trn('Merge all files into a single directory, replicating the unified VFS view'))
    mode_group.add_argument('--keep-structure', action='store_true',
                            help=trn('Retain the original mod directory structure in the output, useful for identifying file sources'))


def init_text_actions_parser(formatter_class, subparsers):
    # Add config subparser
    parser_config = subparsers.add_parser('config',
                                          formatter_class=formatter_class,
                                          help=trn('Configure application settings'))
    parser_config.add_argument('--loglevel', help=trn('Set default log level. (Available: %s)') % ["debug", "info", "warning", "error"])
    parser_config.add_argument('--language', help=trn('Set app language. (Available: %s)') % ["en", "uk"])
    parser_config.add_argument('--show-stacktrace', action=BooleanAction, type=str, default=None,
                               help=trn('Enable/Disable showing error stack trace (Available: True/False)'))
    # validate-encoding | ve
    parser_ve = subparsers.add_parser(VALIDATE_ENCODING, aliases=COMMON_CMD_TO_ALIASES[VALIDATE_ENCODING],
                                      formatter_class=formatter_class,
                                      help=trn('Validate encoding of a file or directory'))
    parser_ve.add_argument('paths', nargs='*', help=trn('Paths to files or directories'))
    # fix-encoding | fe
    fe_help = trn('Fix UTF-8 encoding of a file or directory (Warning: may break encoding if detected wrongly)')
    parser_fe = subparsers.add_parser(FIX_ENCODING, aliases=COMMON_CMD_TO_ALIASES[FIX_ENCODING],
                                      formatter_class=formatter_class, help=fe_help)
    parser_fe.add_argument('paths', nargs='*', help=trn('Paths to files or directories'))
    add_git_override_arguments(parser_fe)
    # validate-xml | vx
    parser_vx = subparsers.add_parser(VALIDATE_XML, aliases=COMMON_CMD_TO_ALIASES[VALIDATE_XML],
                                      formatter_class=formatter_class,
                                      help=trn('Validate XML of a file or directory'))
    parser_vx.add_argument('paths', nargs='*', help=trn('Paths to files or directories'))
    # format-xml | fx
    parser_fx = subparsers.add_parser(FORMAT_XML, aliases=COMMON_CMD_TO_ALIASES[FORMAT_XML],
                                      formatter_class=formatter_class,
                                      help=trn('Format XML of a file or directory'))
    parser_fx.add_argument('paths', nargs='*', help=trn('Paths to files or directories'))
    parser_fx.add_argument('--fix', action='store_true',
                           help=trn('Fix XML issues if possible instead of skipping the file'))
    parser_fx.add_argument('--format-text-entries', action='store_true',
                           help=trn('Format <text> tag contents to resemble in-game appearance'))
    add_git_override_arguments(parser_fx)
    # check-primary-lang | cpl
    parser_cpl = subparsers.add_parser(CHECK_PRIMARY_LANG, aliases=COMMON_CMD_TO_ALIASES[CHECK_PRIMARY_LANG],
                                       formatter_class=formatter_class,
                                       help=trn('Check primary language of a file or directory'))
    parser_cpl.add_argument('paths', nargs='*', help=trn('Paths to files or directories'))
    cpl_help = trn('Language to exclude from the report separated with "+". E.g: [cyan]--exclude uk+en[/cyan]')
    parser_cpl.add_argument('--exclude', dest='exclude', help=cpl_help)
    parser_cpl.add_argument('--detailed', action='store_true',
                            help=trn('Show detailed report with language occurrences per file'))
    # translate | tr
    parser_tr = subparsers.add_parser(TRANSLATE, aliases=COMMON_CMD_TO_ALIASES[TRANSLATE],
                                      formatter_class=formatter_class,
                                      help=trn('Translate text in a file or directory'))
    parser_tr.add_argument('paths', nargs='*', help=trn('Paths to files or directories'))
    parser_tr.add_argument('--from', dest='from_lang', help=trn('Source language (auto-detect if missing)'))
    parser_tr.add_argument('--to', dest='to_lang', required=True, help=trn('Target language'))
    parser_tr.add_argument('--api-key', help=trn("API key for translation service. If absent Google Translation be used (it sucks)"))
    add_git_override_arguments(parser_tr)
    # analyze-patterns | ap
    parser_ap = subparsers.add_parser(ANALYZE_PATTERNS, aliases=COMMON_CMD_TO_ALIASES[ANALYZE_PATTERNS],
                                      formatter_class=formatter_class,
                                      help=trn('Analyze patterns in a file or directory'))
    parser_ap.add_argument('paths', nargs='*', help=trn('Paths to files or directories'))
    parser_ap.add_argument('--save', action='store_true', default=False,
                           help=trn('Save detailed report as JSON file (for future comparison)'))
    # parser_ap.add_argument('--compare', dest='compare_to_path',
    #                        help='Compare freshly-generated analysis with one provided in file')
    # # fix-known-broken-patterns | fbp
    # parser_fbp = subparsers.add_parser(FIX_KNOWN_BROKEN_PATTERNS, aliases=CMD_TO_ALIASES[FIX_KNOWN_BROKEN_PATTERNS],
    #                                    formatter_class=parser.formatter_class,
    #                                    help='Fix known broken patterns in a file or directory')
    # parser_fbp.add_argument('paths', nargs='*', help=t('Paths to files or directories'))
    # add_git_override_arguments(parser_fbp)
    # capitalize-text | ct
    ct_help = trn('Capitalize first letter [cyan](a->A)[/cyan] in all text entries in a file or directory')
    parser_ct = subparsers.add_parser(CAPITALIZE_TEXT, aliases=COMMON_CMD_TO_ALIASES[CAPITALIZE_TEXT],
                                      formatter_class=formatter_class, help=ct_help)
    parser_ct.add_argument('paths', nargs='*', help=trn('Paths to files or directories'))
    add_git_override_arguments(parser_ct)
    # find-string-dups | fsd
    fsd_help = trn(
        "Looks for duplicates of [green]'<string id=\"...\">'[/green] to eliminate unwanted conflicts/overrides. Provides filecentric report by default")
    parser_fsd = subparsers.add_parser(FIND_STRING_DUPLICATES, aliases=COMMON_CMD_TO_ALIASES[FIND_STRING_DUPLICATES],
                                       formatter_class=formatter_class, help=fsd_help)
    parser_fsd.add_argument('--per-string-report', action='store_true', default=False,
                            help=trn('Display detailed report with string text'))
    parser_fsd.add_argument('--web-visualizer', action='store_true', default=False,
                            help=trn('Display duplicates as D3 interactive graph'))
    parser_fsd.add_argument('--save-report', action='store_true', default=False,
                            help=trn('Save filecentric report as JSON'))
    parser_fsd.add_argument('paths', nargs='*', help=trn('Paths to files or directories'))
    # find-string-dups | fsd
    parser_sfwd = subparsers.add_parser(SORT_FILES_WITH_DUPLICATES, aliases=COMMON_CMD_TO_ALIASES[SORT_FILES_WITH_DUPLICATES],
                                        formatter_class=formatter_class,
                                        help=trn("Sorts strings in files alphabetically placing duplicates on top"))
    parser_sfwd.add_argument('--sort-duplicates-only', action='store_true', default=False,
                             help=trn("Don't sort non-duplicates"))
    parser_sfwd.add_argument('paths', nargs='*',
                             help=trn('Paths to two files you want to compare and sort dups'))
    add_git_override_arguments(parser_sfwd)


def handle_config_command(args):
    """Handle the config command to update the settings."""
    config_manager = ConfigFileManager()

    if args.loglevel is not None:
        config_manager.update_config('general', 'loglevel', args.loglevel)
        get_console().print(cf_cyan(trn("Set new default log level to '%s'") % args.loglevel))

    if args.language is not None:
        config_manager.update_config('general', 'language', args.language)
        get_console().print(cf_cyan(trn("Set new app language to '%s'") % args.language))

    if args.show_stacktrace is not None:
        show_stacktrace_value = 'yes' if args.show_stacktrace else 'no'
        config_manager.update_config('general', 'show_stacktrace', show_stacktrace_value)
        if args.show_stacktrace:
            get_console().print(cf_cyan(trn("Stacktrace printing on failure ENABLED")))
        else:
            get_console().print(cf_cyan(trn("Stacktrace printing on failure DISABLED")))


def handle_misc_command(args):
    if args.check_deepl_tokens_usage is not None:
        check_deepl_tokens_usage(args.check_deepl_tokens_usage)


def main():
    new_main()

    start_time = time.process_time()
    try:
        log.debug(trn("Start"))
        args: argparse.Namespace = parse_args()

        # If the command is 'config', handle the configuration update
        if args.command == 'config':
            handle_config_command(args)
        elif args.command == 'misc':
            handle_misc_command(args)
        else:
            process_command(args)
    except Exception as e:
        show_stack_trace = file_config.general.show_stacktrace or False
        if os.environ.get("PY_ST"):
            show_stack_trace = os.environ.get("PY_ST").lower() == 'true'

        if show_stack_trace:
            log.fatal(trn("Failed to perform actions. Error: %s") % traceback.format_exc())
        else:
            log.fatal(trn("Failed to perform actions. Error: %s") % e)

    end_time = time.process_time()
    elapsed_time = end_time - start_time
    log.always(trn("Done! Total time: %s") % cf_green("%.3fs" % elapsed_time))
    get_console().print(check_for_update())


def new_main():
    start_time = time.process_time()
    try:
        log.debug(trn("Start"))
        parser = ExtendedHelpParser(description=trn("app_description"), formatter_class=CustomHelpFormatter)
        root = CommandProcessor([
            Config(),
            ValidateEncoding(),
            FixEncoding(),
            ValidateXml(),
            FormatXml(),
            CheckPrimaryLanguage(),
            Translate(),
            AnalyzePatterns(),
            CapitalizeText(),
            FindStringDuplicates(),
            SortFilesWithDuplicates(),
            Misc()
        ])
        root.setup(parser)

        args = parser.parse_args()
        log.debug(f"Args: {args}")

        if args.command is None:
            cmd_name = sys.argv[0].split("/")[-1] + " -h"
            log.always(trn(f"Please provide args. Use {cf_green(cmd_name)} for help"))
            sys.exit()

        root.execute(args)

    except Exception as e:
        show_stack_trace = file_config.general.show_stacktrace or False
        if os.environ.get("PY_ST"):
            show_stack_trace = os.environ.get("PY_ST").lower() == 'true'

        if show_stack_trace:
            log.fatal(trn("Failed to perform actions. Error: %s") % traceback.format_exc())
        else:
            log.fatal(trn("Failed to perform actions. Error: %s") % e)

    end_time = time.process_time()
    elapsed_time = end_time - start_time
    log.always(trn("Done! Total time: %s") % cf_green("%.3fs" % elapsed_time))

    get_console().print(check_for_update())
    sys.exit(0)


if __name__ == '__main__':
    main()
