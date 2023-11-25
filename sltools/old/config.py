import queue

from sltools.config_file_manager import ConfigFileManager
from sltools.utils.lang_utils import trn

PRIMARY_ENCODING = 'windows-1251'

#######################################
# Constants for common commands names #
#######################################
VALIDATE_ENCODING = 'validate-encoding'
FIX_ENCODING = 'fix-encoding'
VALIDATE_XML = 'validate-xml'
FORMAT_XML = 'format-xml'
CHECK_PRIMARY_LANG = 'check-primary-lang'
TRANSLATE = 'translate'
ANALYZE_PATTERNS = 'analyze-patterns'
CAPITALIZE_TEXT = 'capitalize-text'
FIND_STRING_DUPLICATES = 'find-string-duplicates'
SORT_FILES_WITH_DUPLICATES = 'sort-files-with-duplicates'
FIX_KNOWN_BROKEN_PATTERNS = 'fix-known-broken-patterns'

PROCESS_MO2 = 'mo2'

COMMON_CMD_TO_ALIASES = {
    VALIDATE_ENCODING: ['ve'],
    FIX_ENCODING: ['fe'],
    VALIDATE_XML: ['vx'],
    FORMAT_XML: ['fx'],
    CHECK_PRIMARY_LANG: ['cpl'],
    TRANSLATE: ['tr'],
    ANALYZE_PATTERNS: ['ap'],
    FIX_KNOWN_BROKEN_PATTERNS: ['fbp'],
    CAPITALIZE_TEXT: ['ct'],
    FIND_STRING_DUPLICATES: ['fsd'],
    SORT_FILES_WITH_DUPLICATES: ['sfwd'],
}

####################################
# Constants for MO2 commands names #
####################################
VFS_MAP = 'vfs-map'
VFS_COPY = 'vfs-copy'

MO2_CMD_TO_ALIASES = {
    VFS_MAP: ['vm'],
    VFS_COPY: ['vc'],
}


# CONSTANTS
UNKNOWN_LANG = trn("Unknown")
TOO_LITTLE_DATA = trn("Too little data")

min_recognizable_text_length = 30
text_wrap_width = 80

# For flask server
file_changes_msg_queue = queue.Queue()


class DefaultArgs(object):
    sort_duplicates_only = False
    allow_no_repo = False
    allow_dirty = False
    allow_not_tracked = False
    pass