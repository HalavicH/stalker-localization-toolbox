import sys
from argparse import Namespace

from sltools.commands.analyze_file_language import check_primary_lang
from sltools.commands.analyze_patterns import analyze_patterns
from sltools.commands.capitalize_all_text import capitalize_all_text
from sltools.commands.find_string_duplicates import find_string_duplicates
from sltools.commands.fix_encoding import fix_encoding
from sltools.commands.format_xml import format_xml
from sltools.commands.sort_strings_in_files import sort_files_with_duplicates
from sltools.commands.translate import translate
from sltools.commands.validate_encoding import validate_encoding
from sltools.commands.validate_xml import validate_xml
from sltools.config import *
from sltools.utils.lang_utils import _tr
from sltools.utils.colorize import cf_green
from sltools.utils.error_utils import *
from sltools.utils.git_utils import is_git_available, log_ignore_option, log_skipped_files


def fix_known_broken_patterns(args, is_read_only):
    log.info(f"Running {args.command} with path: {args.paths}")


# Command Registry
COMMAND_REGISTRY = {
    VALIDATE_ENCODING: {"callback": validate_encoding, "read_only": True},
    FIX_ENCODING: {"callback": fix_encoding, "read_only": False},
    VALIDATE_XML: {"callback": validate_xml, "read_only": True},
    FORMAT_XML: {"callback": format_xml, "read_only": False},
    CHECK_PRIMARY_LANG: {"callback": check_primary_lang, "read_only": True},
    TRANSLATE: {"callback": translate, "read_only": False},
    ANALYZE_PATTERNS: {"callback": analyze_patterns, "read_only": True},
    # FIX_KNOWN_BROKEN_PATTERNS: {"callback": fix_known_broken_patterns, "read_only": False},
    CAPITALIZE_TEXT: {"callback": capitalize_all_text, "read_only": False},
    FIND_STRING_DUPLICATES: {"callback": find_string_duplicates, "read_only": True},
    SORT_FILES_WITH_DUPLICATES: {"callback": sort_files_with_duplicates, "read_only": False},
}


def process_command(args: Namespace):
    log.info(_tr("Processing command: %s") % args.command)
    callback_data = COMMAND_REGISTRY.get(args.command)

    if callback_data is None:
        log.error(_tr("Command '%s' is not implemented") % args.command)
        sys.exit(1)

    callback = callback_data["callback"]
    read_only = callback_data["read_only"]

    if not read_only:
        if not args.allow_no_repo:
            if not is_git_available():
                err = _tr("Git is not available on this system. It's vital to have files in a git repo to prevent potential file damage. Please install Git.")
                log.error(err)
                log_ignore_option("--allow-no-repo")
                return False

    # Do actual work
    log.always(_tr("Running command '%s' on paths: '%s'") % (args.command, args.paths))
    callback(args, read_only)

    log.info(cf_green(_tr("Done")))

    log_skipped_files()
    log_saved_errors()
