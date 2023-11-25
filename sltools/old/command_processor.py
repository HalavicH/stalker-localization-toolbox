from argparse import Namespace

from sltools.old.commands.analyze_file_language import check_primary_lang
from sltools.old.commands.analyze_patterns import analyze_patterns
from sltools.old.commands.capitalize_all_text import capitalize_all_text
from sltools.old.commands.find_string_duplicates import find_string_duplicates
from sltools.old.commands.fix_encoding import fix_encoding
from sltools.old.commands.format_xml import format_xml
from sltools.old.commands.mo2.process_mo2 import process_mo2
from sltools.old.commands.utils.common import map_alias_to_command
from sltools.old.commands.utils.process_generic_cmd import process_generic_cmd
from sltools.old.commands.sort_strings_in_files import sort_files_with_duplicates
from sltools.old.commands import translate
from sltools.old.commands.validate_encoding import validate_encoding
from sltools.old.commands.validate_xml import validate_xml
from sltools.old.config import *
from sltools.utils.error_utils import *


def fix_known_broken_patterns(args, is_read_only):
    log.info(f"Running {args.command} with path: {args.paths}")


# Command Registry
COMMON_COMMAND_REGISTRY = {
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
    PROCESS_MO2: {"callback": process_mo2, "read_only": True},
}


def process_command(args: Namespace, registry=COMMON_COMMAND_REGISTRY):
    map_alias_to_command(args, "command", COMMON_CMD_TO_ALIASES)
    process_generic_cmd(args, args.command, registry)
