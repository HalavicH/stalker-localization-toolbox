import re

from sltools.log_config_loader import log
from sltools.utils.lang_utils import _tr

failed_files = {}


def log_and_save_error(file: str, colored_message: str, level: str = 'error'):
    log.error(_tr("File: '%s'") % file)
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
    log.error(_tr("\t\t\tFailed files errors:"))
    log.error("#" * 80)
    for file in failed_files:
        log.error(_tr("File: '%s'") % file)
        for issue in failed_files[file]:
            log.error("\t" + issue)


def display_encoding_error_details(xml_str, error_str):
    # Assume the position is given as a character index in the error message
    match = re.search(r'position (\d+):', error_str)
    if not match:
        log.error(_tr("Could not extract position from error message: %s") % error_str)
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
    log.error(_tr("Illegal character! Error at row %s, column %s:") % (row, col))
    snippet_start = max(0, row - 3)  # Show up to 2 lines before the error
    snippet_end = min(len(lines), row + 2)  # Show up to 2 lines after the error
    for i in range(snippet_start, snippet_end):
        msg = f"{i + 1}: {lines[i]}"
        log.error(_tr("[default]%s[/default]") % msg)
        if i == row - 1:
            log.error(' ' * (col + len(f"{i + 1}: ") - 1) + '-^-')  # Print a caret under the error column


# Interpret and translate errors
def interpret_error(e):
    error_str = str(e)

    # Handle 'Extra content at the end of the document' error
    if "Extra content at the end of the document, line" in error_str:
        line, column, tag = extract_extra_content_args(error_str)
        base_msg = _tr("Extra content at the end of the document, line %s, column %s (tag %s, line %s)")
        return base_msg % (line, column, tag, line)

    # Handle 'Opening and ending tag mismatch' error
    elif "Opening and ending tag mismatch:" in error_str:
        start_tag, end_tag, line1, line2, column = extract_tag_mismatch_args(error_str)
        base_msg = _tr("Opening and ending tag mismatch: %s line %s and %s, line %s, column %s")
        return base_msg % (start_tag, line1, end_tag, line2, column)

    # Handle 'Premature end of data in tag' error
    elif "Premature end of data in tag" in error_str:
        tag, line, column = extract_premature_end_args(error_str)
        base_msg = _tr("Premature end of data in tag %s line %s, column %s")
        return base_msg % (tag, line, column)

    # Handle 'expected '>' error
    elif "expected '>'" in error_str:
        line, column = extract_expected_greater_than_args(error_str)
        base_msg = _tr("Expected '>', line %s, column %s")
        return base_msg % (line, column)

    # Handle 'XML declaration allowed only at the start of the document' error
    elif "XML declaration allowed only at the start of the document" in error_str:
        line, column = extract_xml_declaration_args(error_str)
        base_msg = _tr("XML declaration allowed only at the start of the document, line %s, column %s")
        return base_msg % (line, column)

    # Handle 'Input is not proper UTF-8, indicate encoding' error
    elif "Input is not proper UTF-8, indicate encoding" in error_str:
        base_msg = _tr("Input is not proper UTF-8, indicate encoding")
        return base_msg

    # Handle 'Unsupported encoding' error
    elif "Unsupported encoding" in error_str:
        encoding, line, column = extract_unsupported_encoding_args(error_str)
        base_msg = _tr("Unsupported encoding %s, line %s, column %s")
        return base_msg % (encoding, line, column)

    # Handle 'String not closed expecting " or '' error
    elif "String not closed expecting" in error_str:
        line, column = extract_string_not_closed_args(error_str)
        base_msg = _tr("String not closed, expecting '\"' or ''', line %s, column %s")
        return base_msg % (line, column)

    # No such file error
    elif "[Errno 2] No such file or directory:" in error_str:
        base_msg = _tr("Can't resolve include! No such file or directory: %s")
        return base_msg % (error_str.split("No such file or directory:")[1])

    return _tr("Unknown error: ") + error_str


def extract_extra_content_args(error_str):
    match = re.search(r"Extra content at the end of the document, line (\d+), column (\d+)", error_str)
    if match:
        line = match.group(1)
        column = match.group(2)
        # Assuming tag extraction is needed; modify as per actual error string
        tag = "unknown"
        return line, column, tag
    return None, None, None


def extract_tag_mismatch_args(error_str):
    match = re.search(r"Opening and ending tag mismatch: (\w+) line (\d+) and (\w+), line (\d+), column (\d+)", error_str)
    if match:
        start_tag = match.group(1)
        line1 = match.group(2)
        end_tag = match.group(3)
        line2 = match.group(4)
        column = match.group(5)
        return start_tag, end_tag, line1, line2, column
    return None, None, None, None, None


def extract_premature_end_args(error_str):
    match = re.search(r"Premature end of data in tag (\w+) line (\d+), line (\d+), column (\d+)", error_str)
    if match:
        tag = match.group(1)
        line = match.group(3)  # Assuming line is repeated
        column = match.group(4)
        return tag, line, column
    return None, None, None


def extract_expected_greater_than_args(error_str):
    match = re.search(r"expected '>', line (\d+), column (\d+)", error_str)
    if match:
        line = match.group(1)
        column = match.group(2)
        return line, column
    return None, None


def extract_xml_declaration_args(error_str):
    match = re.search(r"XML declaration allowed only at the start of the document, line (\d+), column (\d+)", error_str)
    if match:
        line = match.group(1)
        column = match.group(2)
        return line, column
    return None, None


def extract_unsupported_encoding_args(error_str):
    match = re.search(r"Unsupported encoding ([\w-]+), line (\d+), column (\d+)", error_str)
    if match:
        encoding = match.group(1)
        line = match.group(2)
        column = match.group(3)
        return encoding, line, column
    return None, None, None


def extract_string_not_closed_args(error_str):
    match = re.search(r"String not closed expecting [\"'] or [\"'], line (\d+), column (\d+)", error_str)
    if match:
        line = match.group(1)
        column = match.group(2)
        return line, column
    return None, None
