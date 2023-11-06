from rich import get_console

from sltools.commands.common import get_xml_files_and_log, process_files_with_progress
from sltools.log_config_loader import log
from sltools.utils.colorize import cf_cyan
from sltools.utils.file_utils import read_xml, save_xml
from sltools.utils.misc import create_table
from sltools.utils.xml_utils import parse_xml_root, to_utf_string_with_proper_declaration, format_xml_string


def capitalize_first_letter(s):
    for index, char in enumerate(s):
        if char.isalpha():  # Check if the character is alphabetic
            return s[:index] + char.upper() + s[index + 1:]  # Capitalize and return
        elif char != ' ' and char != '\n':  # If the character is not a space and not alphabetic, return original string
            return s
    return s  # Return original string if no alphabetic characters are found


def process_file(file_name, results, args):
    counter = 0
    xml_string = read_xml(file_name)
    root = parse_xml_root(xml_string)

    for string_elem in root:
        for text_elem in string_elem:
            orig_text = text_elem.text
            text_elem.text = capitalize_first_letter(orig_text)
            if orig_text != text_elem.text:
                str_id = cf_cyan(string_elem.attrib.get("id"))
                log.info(f"Text of '{str_id}' was capitalize")
                counter += 1

    resulting_xtr = to_utf_string_with_proper_declaration(root)
    formatted_xml_str = format_xml_string(resulting_xtr, file_name)
    save_xml(file_name, formatted_xml_str)

    if counter > 0:
        results.append((file_name, counter))


def display_report(results):
    if len(results) == 0:
        log.always("No files were modified")

    table = create_table(["File", "Cnt"])

    for file, cnt in results:
        table.add_row(file, str(cnt))

    log.always(f"Capitalized text blocks per file. Total files modified: {len(results)}")
    get_console().print(table)


def capitalize_all_text(args, is_read_only):
    files = get_xml_files_and_log(args.paths, "Analyzing patterns for")

    results = []

    process_files_with_progress(files, process_file, results, args, is_read_only)
    log.info(f"Total processed files: {len(files)}")

    display_report(results)
