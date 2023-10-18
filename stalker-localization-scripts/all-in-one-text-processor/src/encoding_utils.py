import threading

import chardet
from thread_utils import get_thread_color

import log_config_loader

log_config_loader.configure_logging()

import logging

logger: logging.Logger = logging.getLogger('main')

# Constants
ALLOWED_ENCODINGS = ['windows-1251', 'ascii']


def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())

    return result['encoding']


def check_encoding(file_path):
    thread_name = threading.current_thread().name
    color = get_thread_color()
    logger.info(f"{color}[Thread {thread_name}] Processing file: {file_path}")
    encoding = detect_encoding(file_path)
    if encoding.lower() not in ALLOWED_ENCODINGS:
        return (file_path, encoding)
    return None
