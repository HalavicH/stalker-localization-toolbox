import re

from src.log_config_loader import log

failed_files = {}


def log_and_save_error(file: str, colored_message: str, level: str = 'error'):
    log.error(f"File: '{file}'")
    log.error("\t" + colored_message)

    # TODO: save and process level
    if failed_files.get(file) is None:
        failed_files[file] = [colored_message]
    else:
        failed_files[file].append(colored_message)


def clear_saved_errors():
    failed_files.clear()


def log_saved_errors():
    if len(failed_files) == 0:
        return

    log.error("#" * 80)
    log.error("\t\t\tFailed files errors:")
    log.error("#" * 80)
    for file in failed_files:
        log.error(f"File: '{file}'")
        for issue in failed_files[file]:
            log.error("\t" + issue)


def display_encoding_error_details(xml_str, error_str):
    # Assume the position is given as a character index in the error message
    match = re.search(r'position (\d+):', error_str)
    if not match:
        log.error(f"Could not extract position from error message: {error_str}")
        return

    position = int(match.group(1))

    # Calculate row and column
    lines = xml_str.split('\n')
    row, col, char_count = 0, 0, 0
    for i, line in enumerate(lines):
        char_count += len(line) + 1  # +1 for the newline character
        if char_count > position:
            row = i + 1  # 1-indexed row number
            col = len(line) - (char_count - position) + 1  # 1-indexed column number
            break

    # Print details
    log.error(f"Illegal character! Error at row {row}, column {col}:")
    snippet_start = max(0, row - 3)  # Show up to 2 lines before the error
    snippet_end = min(len(lines), row + 2)  # Show up to 2 lines after the error
    for i in range(snippet_start, snippet_end):
        msg = f"{i + 1}: {lines[i]}"
        log.error(f"[default]{msg}[/default]")
        if i == row - 1:
            log.error(' ' * (col + len(f"{i + 1}: ") - 1) + '-^-')  # Print a caret under the error column
