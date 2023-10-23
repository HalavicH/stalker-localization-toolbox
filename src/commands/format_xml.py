from src.commands.common import get_xml_files_and_log, process_files_with_progress
from src.utils.colorize import cf_cyan, cf_green
from src.utils.file_utils import read_xml, save_xml
from src.utils.misc import create_pretty_table, exception_originates_from
from src.utils.plain_text_utils import format_text_entry, tabwidth
from src.utils.xml_utils import *

include_example = cf_red('#include "some/other/file.xml"')

error_str = cf_red("Error")


def format_xml_text_entries(text_formatted_xml, indent_level) -> (str, bool):
    was_formatted = False

    root = parse_xml_root(text_formatted_xml)
    for string_elem in root:
        for text_elem in string_elem:
            orig_text = text_elem.text
            text_elem.text = format_text_entry(orig_text, indent_level)
            if orig_text != text_elem.text:
                str_id = cf_cyan(string_elem.attrib.get("id"))
                log.info(f"Text of '{str_id}' was formatted")
                was_formatted = True

    indent(root)

    # Convert the XML tree to a string
    formatted_xml = to_utf_string_with_proper_declaration(root)

    # Add a blank line before comments
    updated_xml_str = add_blank_line_before_comments(formatted_xml)

    return updated_xml_str.strip() + "\n", was_formatted


def process_file(file_path, results, args):
    was_fixed = False
    text_was_formatted = False
    was_formatted = False

    try:
        # Try to open the file to check if it's readable
        with open(file_path, 'r', encoding='windows_1251') as file:
            file.read()

        # Read XML from the file
        xml_string = read_xml(file_path)

        # Fix errors if needed
        fixed_xml = xml_string
        if args.fix:
            fixed_xml = fix_possible_errors(xml_string, file_path)
            if fixed_xml != xml_string:
                log.debug("Fixed typical XML errors")
                was_fixed = True

        # Format the document
        formatted = format_xml_string(fixed_xml, file_path)
        if formatted != fixed_xml:
            log.debug("Formatted XML schema")
            was_formatted = True

        # Optionally format text entries
        text_formatted_xml = formatted
        if args.format_text_entries:
            text_formatted_xml, any_entry_formatted = format_xml_text_entries(text_formatted_xml, tabwidth * 3)
            if any_entry_formatted:
                log.debug("Formatted <text> entries")
                text_was_formatted = True

        # Save the XML back to the file
        save_xml(file_path, text_formatted_xml)

        if any([was_fixed, text_was_formatted, was_formatted]):
            was_fix_status = to_yes_no(was_fixed) if args.fix else cf_cyan("Disabled")
            was_text_form_status = to_yes_no(text_was_formatted) if args.format_text_entries else cf_cyan("Disabled")
            formatted_status = to_yes_no(was_formatted)
            results.append((file_path, was_fix_status, was_text_form_status, formatted_status))

    except Exception as e:
        if args.fix and exception_originates_from("fix_possible_errors", e):
            was_fix_status = error_str
        else:
            was_fix_status = cf_cyan("Disabled") if not args.fix else "No"

        if args.format_text_entries and exception_originates_from("format_xml_text_entries", e):
            was_text_form_status = error_str
        else:
            was_text_form_status = cf_cyan("Disabled") if not args.format_text_entries else "-"

        if was_text_form_status == error_str:
            formatted_status = cf_cyan("N/a")
        else:
            formatted_status = error_str

        results.append((file_path, was_fix_status, was_text_form_status, formatted_status))
        log_and_save_error(file_path, f"Unhandled error {e}")


def to_yes_no(b: bool) -> str:
    return cf_green("Yes") if b else "No"


def format_xml(args, is_read_only):
    apply_fix = args.fix
    format_text_entries = args.format_text_entries

    if apply_fix:
        log.always(cf_cyan("Fix option enabled. Will fix:"
                           "\n\t- Guard '--' in comments,"
                           "\n\t- Ampersand misuse (& -> &amp;),"
                           "\n\t- Resolve #include"
                           "\n\t- Wrong/missing XML declaration"))

    if format_text_entries:
        log.always(cf_cyan(
            "Format <text> content option enabled. Will make text look as similar as possible to the in-game text"))

    files = get_xml_files_and_log(args.paths, "Formatting XML-schema for")

    results = []
    process_files_with_progress(files, process_file, results, args, is_read_only)

    log.info(f"Total processed files: {len(files)}")
    if len(results) > 0:
        print_report(results, apply_fix, format_text_entries)  # Assuming print_report_format_xml exists
    else:
        silly_message = cf_red("You've just wasted your CPU cycles 😈")
        log.always(cf_green(f"No files required formatting. {silly_message}"))


def print_report(results, apply_fix, format_text_entries):
    failed_files = []
    table_title = cf_cyan(f"Files which were requiring some fixes/formatting (total: {len(results)})")
    column_names = ["Filename", "Fixed", "Formatted <text>", "Formatted"]
    table = create_pretty_table(column_names)

    for filename, fix, text_form, form in results:
        table.add_row([filename, fix, text_form, form])
        if fix == error_str or text_form == error_str or form == error_str:
            failed_files.append(filename)

    log.always(table_title + "\n" + str(table))  # PrettyTable objects can be converted to string using str()

    if len(failed_files) > 0:
        log.always(cf_cyan("These files has syntax/other errors in them, so they wasn't formatted."))
        for file in failed_files:
            log.always(f"\t{cf_yellow(file)}")
        log.always(cf_cyan("Run command with --fix option to try fix errors automatically\n"))
