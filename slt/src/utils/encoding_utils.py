import chardet

from src.log_config_loader import log
from src.utils.colorize import cf_green, cf_yellow, cf_red

# Constants
ALLOWED_ENCODINGS = ['windows-1251', 'ascii']


def is_ascii(binary_text, file_path=""):
    try:
        binary_text.decode('ascii')
        return True
    except UnicodeDecodeError as e:
        log.debug(f"Can't decode file {file_path} as ascii. Error {e}")
        return False


def detect_encoding(binary_text):
    result = chardet.detect(binary_text)

    return result['encoding']


def is_windows_1251_decodable(binary_text, file_path=""):
    try:
        # Attempt to decode the file with windows-1251 encoding
        binary_text.decode('windows-1251')
        return True  # Successfully decoded with windows-1251
    except UnicodeDecodeError as e:
        log.debug(f"Can't decode file {file_path} as windows-1251. Error {e}")
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
