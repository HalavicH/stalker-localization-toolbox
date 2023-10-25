import git

import sys
from argparse import Namespace

from src.commands.analyze_file_language import check_primary_lang
from src.commands.analyze_patterns import analyze_patterns
from src.commands.capitalize_all_text import capitalize_all_text
from src.commands.format_xml import format_xml
from src.commands.fix_encoding import fix_encoding
from src.commands.translate import translate
from src.commands.validate_xml import validate_xml
from src.utils.error_utils import *
from src.config import *
from src.commands.validate_encoding import validate_encoding
from src.utils.colorize import cf_green
from src.log_config_loader import log
from src.utils.git_utils import is_git_available, log_ignore_option, log_skipped_files


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
}


def process_command(args: Namespace):
    log.info(f"Processing command: {args.command}")
    callback_data = COMMAND_REGISTRY.get(args.command)

    callback = callback_data["callback"]
    read_only = callback_data["read_only"]

    if callback is None:
        log.error(f"Command {args.command} is not implemented")
        sys.exit(1)

    if not read_only:
        if not args.allow_no_repo:
            if not is_git_available():
                log.error(
                    "Git is not available on this system. It's vital to have files in a git repo to prevent potential file damage. Please install Git.")
                log_ignore_option("--allow-no-repo")
                return False

    # Do actual work
    log.always(f"Running command '{args.command}' on paths: {args.paths}")
    callback(args, read_only)

    log.info(cf_green("Done"))

    log_skipped_files()
    log_saved_errors()
