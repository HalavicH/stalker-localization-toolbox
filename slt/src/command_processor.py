import sys
import time
from argparse import Namespace

from src.command_names import *
from src.log_config_loader import get_main_logger
from src.utils.colorize import cf_green

log = get_main_logger()


# Define functions for each command
def validate_encoding(args):
    log.info(f"Running {args.command} with path: {args.path}")


def fix_encoding(args):
    log.info(f"Running {args.command} with path: {args.path}")


def validate_xml(args):
    log.info(f"Running {args.command} with path: {args.path}")


def format_xml(args):
    log.info(f"Running {args.command} with path: {args.path}")


def check_primary_lang(args):
    log.info(f"Running {args.command} with path: {args.path}")


def translate(args):
    log.info(
        f"Running {args.command} with path: {args.path}, from_lang: {args.from_lang}, to_lang: {args.to_lang}, api_key: {args.api_key}")


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

    callback(args)

    log.info(cf_green("Done"))

