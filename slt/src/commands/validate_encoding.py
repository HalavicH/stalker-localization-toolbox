from src.commands.common import get_xml_files_and_log, process_files_with_progress
from src.log_config_loader import log
from src.utils.colorize import cf_green, cf_red
from src.utils.encoding_utils import detect_encoding, is_file_content_win1251_compatible
from src.utils.misc import create_pretty_table


def process_file(file, results: list):
    with open(file, 'rb') as f:
        binary_text = f.read()

    encoding = detect_encoding(binary_text)
    compatible, comment = is_file_content_win1251_compatible(binary_text, encoding)
    if compatible:
        log.debug(f"File {file} is ok. Encoding: {encoding}")
        return

    results.append((file, encoding, comment))


def validate_encoding(args):
    files = get_xml_files_and_log(args.paths, "Validating encoding for")

    results = []
    process_files_with_progress(files, process_file, results)  # Assuming process_file_validate_encoding exists

    log.info(f"Total processed files: {len(files)}")
    display_report(results)


def display_report(report):
    if len(report) == 0:
        log.info(cf_green("No files with bad encoding detected!"))
        return

    report = sorted(report, key=lambda tup: tup[1])  # Sorting based on encoding

    table_title = cf_red(f"Files with possibly incompatible/broken encoding (total: {len(report)})")
    column_names = ["Filename", "Encoding", "Comment"]
    table = create_pretty_table(column_names)

    for filename, encoding, comment in report:
        table.add_row([filename, encoding, comment])

    log.always(table_title + "\n" + str(table))  # PrettyTable objects can be converted to string using str()
