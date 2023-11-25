import chardet

from sltools.config import PRIMARY_ENCODING
from sltools.log_config_loader import log
from sltools.utils.colorize import cf_green, cf_yellow, cf_red
from sltools.utils.lang_utils import trn

# Constants
ALLOWED_ENCODINGS = [PRIMARY_ENCODING, 'ascii']


def is_ascii(binary_text, file_path=""):
    try:
        binary_text.decode('ascii')
        return True
    except UnicodeDecodeError as e:
        log.debug(trn("Can't decode file %s as ascii. Error %s") % (file_path, e))
        return False


def detect_encoding(binary_text):
    result = chardet.detect(binary_text)

    return result['encoding']


def is_windows_1251_decodable(binary_text, file_path=""):
    try:
        # Attempt to decode the file with windows-1251 encoding
        binary_text.decode(PRIMARY_ENCODING)
        return True  # Successfully decoded with windows-1251
    except UnicodeDecodeError as e:
        log.debug(trn("Can't decode file %s as windows-1251. Error %s") % (file_path, e))
        return False  # Decoding error occurred, not compatible with windows-1251


def is_file_content_win1251_compatible(binary_text, encoding):
    if encoding in ALLOWED_ENCODINGS:
        return True, cf_green("All good")
    elif is_ascii(binary_text):
        return True, cf_green("All good")
    elif is_windows_1251_decodable(binary_text):
        return False, cf_yellow("Suspicious")
    else:
        return False, cf_red("Not decodable")
