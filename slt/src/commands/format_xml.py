from rich.progress import Progress

from src.utils.file_utils import find_xml_files, read_xml, save_xml
from src.utils.misc import get_term_width
from src.utils.xml_utils import *

include_example = cf_red('#include "some/other/file.xml"')


def process_file(file_path):
    try:
        with open(file_path, 'r', encoding=windows_1251) as file:
            file.read()
    except UnicodeDecodeError as e:
        msg = f"Can't open file {file_path} as {windows_1251} encoded. Error: {e}"
        log_and_save_error(file_path, msg)

    xml_string = read_xml(file_path)

    formatted = format_xml_string(xml_string, file_path)

    save_xml(file_path, formatted)


def format_xml(args):
    files = find_xml_files(args.path)
    log.always(f"Formatting XML-schema for {cf_green(len(files))} files")

    term_width = get_term_width()
    if term_width > 130:
        max_file_width = term_width - 80
    else:
        max_file_width = term_width - 60

    with Progress() as progress:
        task = progress.add_task("Processing...", total=len(files))
        for i, file_path in enumerate(files):
            # Truncate the file_path path if it exceeds the maximum width
            truncated_file = (
                "..." + file_path[-(max_file_width - 5):]
                if len(file_path) > max_file_width
                else file_path.ljust(max_file_width)
            )

            # Update the progress bar with the truncated description
            progress.update(task, completed=i,
                            description=f"Processing file_path [green]#{i:03}[/] with name [green]{truncated_file}[/]")

            log.debug(f"Processing file #{i}")
            try:
                process_file(file_path)
            except Exception as e:
                log_and_save_error(file_path, f"Unhandled error {e}")
        log.info(f"Total processed files: {len(files)}")


def print_report(results):
    sorted_results = sorted(results, key=lambda x: x[0])

    log.always(('#' * 100))
    log.always(cf_red(f'\t\t\t\t\t Found {len(results)} invalid files:'))
    log.always(('#' * 100))

    for file, issues in sorted_results:
        log.always(f'File: {cf_green(file)}')
        log.always(cf_yellow(f'Issues:'))
        for issue in issues:
            log.always(cf_yellow(f'\t{issue}'))
