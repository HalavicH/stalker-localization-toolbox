from rich.progress import Progress

from prettytable import PrettyTable

from src.log_config_loader import log
from src.utils.colorize import cf_green, cf_red
from src.utils.encoding_utils import detect_encoding, is_file_content_win1251_compatible
from src.utils.file_utils import find_xml_files
from src.utils.misc import get_term_width


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
    files = find_xml_files(args.path)
    log.always(f"Validating encoding for {cf_green(len(files))} files")

    term_width = get_term_width()
    if term_width > 130:
        max_file_width = term_width - 80
    else:
        max_file_width = term_width - 60


    results = []
    with Progress() as progress:
        task = progress.add_task("Processing...", total=len(files))
        for i, file in enumerate(files):
            # Truncate the file path if it exceeds the maximum width
            truncated_file = (
                "..." + file[-(max_file_width - 5):]
                if len(file) > max_file_width
                else file.ljust(max_file_width)
            )

            # Update the progress bar with the truncated description
            progress.update(task, completed=i,
                            description=f"Processing file [green]#{i:03}[/] with name [green]{truncated_file}[/]")

            log.debug(f"Processing file #{i}")
            process_file(file, results)
        log.info(f"Total processed files: {len(files)}")

    if len(results) > 0:
        sorted_results = sorted(results, key=lambda tup: tup[1], reverse=True)

        print_table(sorted_results)
    else:
        log.info(cf_green("No files with bad encoding detected!"))

    return results
