from rich import get_console
from sltools.commands.utils.common import get_xml_files_and_log, process_files_with_progress
from sltools.log_config_loader import log
from sltools.utils.colorize import cf_green, cf_red
from sltools.utils.encoding_utils import detect_encoding, is_file_content_win1251_compatible
from sltools.utils.misc import create_table
from sltools.utils.lang_utils import trn  # Ensure this import is included for _tr function


def process_file(file, results: list, args):
    with open(file, 'rb') as f:
        binary_text = f.read()

    encoding = detect_encoding(binary_text)
    compatible, comment = is_file_content_win1251_compatible(binary_text, encoding)
    if compatible:
        log.debug(trn("File %s is ok. Encoding: %s") % (file, encoding))
        return

    results.append((file, encoding, comment))


def validate_encoding(args, is_read_only):
    files = get_xml_files_and_log(args.paths, trn("Validating encoding for"))

    results = []
    process_files_with_progress(files, process_file, results, args, is_read_only)

    log.info(trn("Total processed files: %d") % len(files))
    display_report(results)
    return results


def display_report(report):
    if len(report) == 0:
        log.info(cf_green(trn("No files with bad encoding detected!")))
        return

    report = sorted(report, key=lambda tup: tup[1])  # Sorting based on encoding

    table_title = cf_red(trn("Files with possibly incompatible/broken encoding (total: %d)") % len(report))
    column_names = [trn("Filename"), trn("Encoding"), trn("Comment")]
    table = create_table(column_names)

    for filename, encoding, comment in report:
        table.add_row(filename, encoding, comment)

    log.always(table_title)
    get_console().print(table)
