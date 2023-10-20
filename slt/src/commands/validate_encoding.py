import os

from prettytable import PrettyTable

from src.log_config_loader import log
from src.utils.colorize import cf_green, cf_red
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
        terminal_width = os.get_terminal_size().columns - 5
    except OSError:
        terminal_width = 160

    table_title = cf_red(f"Files with possibly incompatible/broken encoding (total: {len(data)})")
    column_names = ["Filename", "Encoding", "Comment"]
    table = create_pretty_table(column_names)

    for filename, encoding, comment in data:
        table.add_row([filename, encoding, comment])

    log.always(table_title + "\n" + str(table))  # PrettyTable objects can be converted to string using str()


def create_pretty_table(columns, title=None):
    table = PrettyTable()
    if title is not None:
        table.title = title
    table.field_names = columns
    table.align = 'l'
    table.border = True

    # Basic lines
    table.vertical_char = u'\u2502'  # Vertical line
    table.horizontal_char = u'\u2500'  # Horizontal line
    table._horizontal_align_char = None  # Default is None, setting it explicitly for clarity
    table.junction_char = u'\u253C'  # Plus

    # Corner characters for smooth edges
    table.top_left_junction_char = u'\u256D'  # Rounded top-left corner
    table.top_right_junction_char = u'\u256E'  # Rounded top-right corner
    table.bottom_left_junction_char = u'\u2570'  # Rounded bottom-left corner
    table.bottom_right_junction_char = u'\u256F'  # Rounded bottom-right corner

    # Junction characters for T-junctions
    table.top_junction_char = u'\u252C'  # T-junction facing down
    table.bottom_junction_char = u'\u2534'  # T-junction facing up
    table.left_junction_char = u'\u251C'  # T-junction facing right
    table.right_junction_char = u'\u2524'  # T-junction facing left
    return table


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
