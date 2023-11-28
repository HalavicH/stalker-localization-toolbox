import queue

from sltools.utils.lang_utils import trn

PRIMARY_ENCODING = 'windows-1251'

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
