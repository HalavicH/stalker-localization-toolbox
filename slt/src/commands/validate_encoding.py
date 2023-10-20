import os
import re

from rich.console import Console
from rich.table import Table

from src.log_config_loader import log
from src.utils.colorize import cf_green
from src.utils.encoding_utils import detect_encoding, is_file_content_win1251_compatible
from src.utils.file_utils import find_xml_files

def process_file(file, results: list):
    with open(file, 'rb') as f:
        binary_text = f.read()

    encoding = detect_encoding(binary_text)
    compatible, comment = is_file_content_win1251_compatible(binary_text, encoding)
    if compatible:
        log.debug(f"File {file} is ok. Encoding: {encoding}")
        return

    results.append((file, encoding, comment))


def print_table(data):
    try:
        terminal_width = os.get_terminal_size().columns -5
    except OSError:
        terminal_width = 160

    table = Table(title=f"Files with incompatible broken encoding (total: {len(data)})", width=terminal_width)

    table.add_column("Filename")
    table.add_column("Encoding", min_width=len("Encoding"))
    table.add_column("Comment", min_width=len("Comment"))

    for filename, encoding, comment in data:
        table.add_row(filename, encoding, comment)

    log.info(f"Found files with broken encoding")
    console = Console()
    # Add to log
    console.print(table.expo)


def validate_encoding(args):
    log.info(f"Running {args.command} with path: {args.path}")
    files = find_xml_files(args.path)

    results = []
    for i, file in enumerate(files):
        log.info(f"Processing file #{i}")
        process_file(file, results)
    log.info(f"Total processed files: {len(files)}")

    if len(results) > 0:
        sorted_results = sorted(results, key=lambda tup: tup[1], reverse=True)

        print_table(sorted_results)
    else:
        log.info(cf_green("No files with bad encoding detected!"))
