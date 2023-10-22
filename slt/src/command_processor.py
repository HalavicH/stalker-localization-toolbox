
import sys
from argparse import Namespace

from src.commands.analyze_file_language import check_primary_lang
from src.commands.format_xml import format_xml
from src.commands.fix_encoding import fix_encoding
from src.commands.translate import translate
from src.commands.validate_xml import validate_xml
from src.utils.error_utils import *
from src.command_names import *
from src.commands.validate_encoding import validate_encoding
from src.utils.colorize import cf_green
from src.log_config_loader import log


def analyze_patterns(args):
    log.info(f"Running {args.command} with path: {args.path}")


def fix_known_broken_patterns(args):
    log.info(f"Running {args.command} with path: {args.path}")


# Command Registry
COMMAND_REGISTRY = {
    VALIDATE_ENCODING: validate_encoding,
    FIX_ENCODING: fix_encoding,
    VALIDATE_XML: validate_xml,
    FORMAT_XML: format_xml,
    CHECK_PRIMARY_LANG: check_primary_lang,
    TRANSLATE: translate,
    ANALYZE_PATTERNS: analyze_patterns,
    FIX_KNOWN_BROKEN_PATTERNS: fix_known_broken_patterns,
}


def process_command(args: Namespace):
    log.info(f"Processing command: {args.command}")
    callback = COMMAND_REGISTRY.get(args.command)

    if callback is None:
        log.error(f"Command {args.command} is not implemented")
        sys.exit(1)

    # Do actual work
    log.always(f"Running command '{args.command}' on path: '{args.path}'")
    callback(args)

    log.info(cf_green("Done"))

    log_saved_errors()
