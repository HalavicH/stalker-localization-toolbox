from rich import get_console

from sltools.commands.utils.common import get_xml_files_and_log, process_files_with_progress
from sltools.utils.colorize import cf_cyan, cf_green
from sltools.utils.file_utils import read_xml, save_xml
from sltools.utils.misc import create_table, exception_originates_from
from sltools.utils.plain_text_utils import format_text_entry, tabwidth
from sltools.utils.xml_utils import *
from sltools.utils.lang_utils import _tr

error_str = cf_red(_tr("Error"))


def format_xml_text_entries(text_formatted_xml, indent_level) -> (str, bool):
    was_formatted = False

    root = parse_xml_root(text_formatted_xml)
    for string_elem in root:
        for text_elem in string_elem:
            orig_text = text_elem.text
            text_elem.text = format_text_entry(orig_text, indent_level)
            if orig_text != text_elem.text:
                str_id = cf_cyan(string_elem.attrib.get("id"))
                log.info(_tr("Text of '%s' was formatted") % str_id)
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
                log.debug(_tr("Fixed typical XML errors"))
                was_fixed = True

        # Format the document
        formatted = format_xml_string(fixed_xml, file_path)
        if formatted != fixed_xml:
            log.debug(_tr("Formatted XML schema"))
            was_formatted = True

        # Optionally format text entries
        text_formatted_xml = formatted
        if args.format_text_entries:
            text_formatted_xml, any_entry_formatted = format_xml_text_entries(text_formatted_xml, tabwidth * 3)
            if any_entry_formatted:
                log.debug(_tr("Formatted <text> entries"))
                text_was_formatted = True

        # Save the XML back to the file
        save_xml(file_path, text_formatted_xml)

        if any([was_fixed, text_was_formatted, was_formatted]):
            was_fix_status = to_yes_no(was_fixed) if args.fix else cf_cyan(_tr("Disabled"))
            was_text_form_status = to_yes_no(text_was_formatted) if args.format_text_entries else cf_cyan(_tr("Disabled"))
            formatted_status = to_yes_no(was_formatted)
            results.append((file_path, was_fix_status, was_text_form_status, formatted_status))

    except Exception as e:
        if args.fix and exception_originates_from("fix_possible_errors", e):
            was_fix_status = error_str
        else:
            was_fix_status = cf_cyan(_tr("Disabled")) if not args.fix else _tr("No")
        if args.format_text_entries and exception_originates_from("format_xml_text_entries", e):
            was_text_form_status = error_str
        else:
            was_text_form_status = cf_cyan(_tr("Disabled")) if not args.format_text_entries else "-"
        if was_text_form_status == error_str:
            formatted_status = cf_cyan(_tr("N/a"))
        else:
            formatted_status = error_str
        results.append((file_path, was_fix_status, was_text_form_status, formatted_status))
        log_and_save_error(file_path, _tr("Unhandled error %s") % e)


def to_yes_no(b: bool) -> str:
    return cf_green(_tr("Yes")) if b else _tr("No")


def format_xml(args, is_read_only):
    apply_fix = args.fix
    format_text_entries = args.format_text_entries

    if apply_fix:
        log.always(cf_cyan(_tr("Fix option enabled. Will fix:") +
                           _tr("\n\t- Guard '--' in comments,") +
                           _tr("\n\t- Ampersand misuse (& -> &amp;),") +
                           _tr("\n\t- Resolve #include") +
                           _tr("\n\t- Wrong/missing XML declaration")))

    if format_text_entries:
        log.always(cf_cyan(_tr("Format <text> content option enabled. Will make text look as similar as possible to the in-game text")))

    files = get_xml_files_and_log(args.paths, _tr("Formatting XML-schema for"))

    results = []
    process_files_with_progress(files, process_file, results, args, is_read_only)

    log.info(_tr("Total processed files: %d") % len(files))
    if len(results) > 0:
        print_report(results, apply_fix, format_text_entries)  # Assuming print_report_format_xml exists
    else:
        silly_message = cf_red(_tr("You've just wasted your CPU cycles 😈"))
        log.always(cf_green(_tr("No files required formatting. %s")) % silly_message)


def print_report(results, apply_fix, format_text_entries):
    failed_files = []
    table_title = cf_cyan(_tr("Files which were requiring some fixes/formatting (total: %d)") % len(results))
    column_names = [_tr("Filename"), _tr("Fixed"), _tr("Formatted <text>"), _tr("Formatted")]
    table = create_table(column_names)

    for filename, fix, text_form, form in results:
        table.add_row(filename, fix, text_form, form)
        if fix == error_str or text_form == error_str or form == error_str:
            failed_files.append(filename)

    log.always(table_title)
    get_console().print(table)

    if len(failed_files) > 0:
        log.always(cf_cyan(_tr("These files have syntax/other errors in them, so they weren't formatted.")))
        for file in failed_files:
            log.always("\t%s" % cf_yellow(file))
        log.always(cf_cyan(_tr("Run command with --fix option to try to fix errors automatically\n")))
