from lxml import etree
from rich import get_console

from sltools.baseline.command_baseline import AbstractCommand
from sltools.log_config_loader import log
from sltools.root_commands.FormatXml import to_yes_no, error_str, format_xml_text_entries
from sltools.utils.colorize import cf_green, cf_red, cf_yellow, cf_cyan
from sltools.utils.error_utils import log_and_save_error
from sltools.utils.file_utils import read_xml, save_xml
from sltools.utils.git_utils import is_allowed_to_continue
from sltools.utils.lang_utils import trn
from sltools.utils.misc import create_table, exception_originates_from, create_equal_length_comment_line
from sltools.utils.plain_text_utils import tabwidth, format_text_entry
from sltools.utils.xml_utils import fix_possible_errors, format_xml_string, parse_xml_root, indent, to_utf_string_with_proper_declaration, \
    add_blank_line_before_comments


def sort_and_save_file(duplicates, file_path, root, sort_duplicates_only):
    log.info(trn("Processing file: '%s'") % file_path)
    sort_strings_by_id(root, duplicates, sort_duplicates_only)
    # For each file use to save the files
    resulting_xtr = to_utf_string_with_proper_declaration(root)
    formatted_xml_str = format_xml_string(resulting_xtr, file_path)
    save_xml(file_path, formatted_xml_str)
    log.info(trn("Done with file: '%s'") % file_path)


def find_common_string_ids(root1, root2):
    # Get dict of elem.get("id") to elem.find("text").text
    string_ids1 = {elem.get("id"): elem.find("text").text for elem in root1.iter("string")}

    # Get map of elem.get("id") to elem.find("text").text
    string_ids2 = {elem.get("id"): elem.find("text").text for elem in root2.iter("string")}

    # Find common string IDs (duplicates) between the two sets
    common_ids = set(string_ids1.keys()).intersection(string_ids2.keys())

    # Create dict of id to True if they have the same text, else False
    duplicates = {string_id: string_ids1[string_id] == string_ids2[string_id] for string_id in common_ids}

    return duplicates


def sort_strings_by_id(root, duplicates, sort_duplicates_only):
    # Create a dictionary to store invalid tags/comments
    elem_to_comments = {}

    # Create a list to hold the sorted <string id=""> elements
    sorted_string_elements = []
    different_duplicates = []
    identical_duplicates = []

    # Create a list to temporarily store invalid tags/comments
    comments_per_elem = []

    for elem in root:
        if elem.tag == "string" and elem.get("id") is not None:
            string_id = elem.get("id")

            # If it's a <string id=""> element, add it to the list
            if string_id in duplicates.keys():
                if duplicates[string_id] is True:
                    identical_duplicates.append(elem)
                else:
                    different_duplicates.append(elem)
            else:
                sorted_string_elements.append(elem)

            # Add the collected invalid tags/comments to the dictionary and clear the list
            if string_id in elem_to_comments:
                elem_to_comments[string_id].extend(comments_per_elem)
            else:
                elem_to_comments[string_id] = comments_per_elem
            comments_per_elem = []
        else:
            # If it's not a <string id=""> element, add it to the comments_per_elem list
            comments_per_elem.append(elem)

    # Sort the elements alphabetically by their "id" attribute (string id)
    if not sort_duplicates_only:
        log.info(trn("Sorting all entries instead of only duplicates"))
        sorted_string_elements.sort(key=lambda elem: elem.get("id", ""))
    different_duplicates.sort(key=lambda elem: elem.get("id", ""))
    identical_duplicates.sort(key=lambda elem: elem.get("id", ""))

    # Remove all elements from the root
    root.clear()

    # Add the sorted elements back to the root, preserving comments
    identical_comment = trn('Identical duplicated strings (safe to delete one of them)')
    different_comment = trn('Duplicated string IDs with different content (requires inspection)')
    unique_comment = trn('Unique string IDs (keeping as is)')

    root.append(etree.Comment(create_equal_length_comment_line(identical_comment)))
    root.append(etree.Comment(identical_comment))
    root.append(etree.Comment(create_equal_length_comment_line(identical_comment)))
    populate_elements(elem_to_comments, root, identical_duplicates)

    root.append(etree.Comment(create_equal_length_comment_line(different_comment)))
    root.append(etree.Comment(different_comment))
    root.append(etree.Comment(create_equal_length_comment_line(different_comment)))
    populate_elements(elem_to_comments, root, different_duplicates)

    root.append(etree.Comment(create_equal_length_comment_line(unique_comment)))
    root.append(etree.Comment(unique_comment))
    root.append(etree.Comment(create_equal_length_comment_line(unique_comment)))
    populate_elements(elem_to_comments, root, sorted_string_elements)


def populate_elements(invalid_elements, root, sorted_elements):
    for elem in sorted_elements:
        string_id = elem.get("id")
        if string_id in invalid_elements:
            for comment in invalid_elements[string_id]:
                log.debug(trn("appending %s") % etree.tostring(comment, pretty_print=True))
                root.append(comment)
        log.debug(trn("appending %s") % etree.tostring(elem, pretty_print=True))
        root.append(elem)


class SortFilesWithDuplicates(AbstractCommand):
    # Metadata
    ##########
    def get_name(self) -> str:
        return "sort-files-with-duplicates"

    def get_aliases(self) -> list:
        return ['sfwd']

    def _get_help(self) -> str:
        return trn("Sorts strings in files alphabetically placing duplicates on top")

    def _setup_parser_args(self, parser):
        parser.add_argument('--sort-duplicates-only', action='store_true', default=False,
                            help=trn("Don't sort non-duplicates"))
        parser.add_argument('paths', nargs='*',
                            help=trn('Paths to two files you want to compare and sort dups'))
        self._add_git_override_arguments(parser)

    # Execution
    ###########
    def _process_file(self, file_path, results: dict, args):
        was_fixed = False
        text_was_formatted = False
        was_formatted = False

        report = results["report"]
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
                    log.debug(trn("Fixed typical XML errors"))
                    was_fixed = True

            # Format the document
            formatted = format_xml_string(fixed_xml, file_path)
            if formatted != fixed_xml:
                log.debug(trn("Formatted XML schema"))
                was_formatted = True

            # Optionally format text entries
            text_formatted_xml = formatted
            if args.format_text_entries:
                text_formatted_xml, any_entry_formatted = format_xml_text_entries(text_formatted_xml, tabwidth * 3)
                if any_entry_formatted:
                    log.debug(trn("Formatted <text> entries"))
                    text_was_formatted = True

            # Save the XML back to the file
            save_xml(file_path, text_formatted_xml)

            if any([was_fixed, text_was_formatted, was_formatted]):
                was_fix_status = to_yes_no(was_fixed) if args.fix else cf_cyan(trn("Disabled"))
                was_text_form_status = to_yes_no(text_was_formatted) if args.format_text_entries else cf_cyan(trn("Disabled"))
                formatted_status = to_yes_no(was_formatted)
                report.append((file_path, was_fix_status, was_text_form_status, formatted_status))

        except Exception as e:
            if args.fix and exception_originates_from("fix_possible_errors", e):
                was_fix_status = error_str
            else:
                was_fix_status = cf_cyan(trn("Disabled")) if not args.fix else trn("No")
            if args.format_text_entries and exception_originates_from("format_xml_text_entries", e):
                was_text_form_status = error_str
            else:
                was_text_form_status = cf_cyan(trn("Disabled")) if not args.format_text_entries else "-"
            if was_text_form_status == error_str:
                formatted_status = cf_cyan(trn("N/a"))
            else:
                formatted_status = error_str
            report.append((file_path, was_fix_status, was_text_form_status, formatted_status))
            log_and_save_error(file_path, trn("Unhandled error %s") % e)

    @staticmethod
    def format_xml_text_entries(text_formatted_xml, indent_level) -> (str, bool):
        was_formatted = False

        root = parse_xml_root(text_formatted_xml)
        for string_elem in root:
            for text_elem in string_elem:
                orig_text = text_elem.text
                text_elem.text = format_text_entry(orig_text, indent_level)
                if orig_text != text_elem.text:
                    str_id = cf_cyan(string_elem.attrib.get("id"))
                    log.info(trn("Text of '%s' was formatted") % str_id)
                    was_formatted = True

        indent(root)

        # Convert the XML tree to a string
        formatted_xml = to_utf_string_with_proper_declaration(root)

        # Add a blank line before comments
        updated_xml_str = add_blank_line_before_comments(formatted_xml)

        return updated_xml_str.strip() + "\n", was_formatted

    def execute(self, args) -> dict:
        file_path1 = args.paths[0]
        file_path2 = args.paths[1]
        sort_duplicates_only = args.sort_duplicates_only

        if not is_allowed_to_continue(file_path1, args.allow_no_repo, args.allow_dirty, args.allow_not_tracked):
            return {}
        if not is_allowed_to_continue(file_path2, args.allow_no_repo, args.allow_dirty, args.allow_not_tracked):
            return {}

        log.info(trn("Sorting files: '%s' and '%s'") % (file_path1, file_path2))

        # Parse XML roots for both files
        xml_tree1 = read_xml(file_path1)
        root1 = parse_xml_root(xml_tree1)
        xml_tree2 = read_xml(file_path2)
        root2 = parse_xml_root(xml_tree2)

        duplicates = find_common_string_ids(root1, root2)
        log.info(trn("Found %s duplicates" % len(duplicates.keys())))

        sort_and_save_file(duplicates, file_path1, root1, sort_duplicates_only)
        sort_and_save_file(duplicates, file_path2, root2, sort_duplicates_only)

        return {}

    # Displaying
    ############
    def display_result(self, result: dict):
        report: list = result["report"]
        if len(report) == 0:
            silly_message = cf_red(trn("You've just wasted your CPU cycles 😈"))
            log.always(cf_green(trn("No files required formatting. %s")) % silly_message)
            return

        failed_files = []
        table_title = cf_cyan(trn("Files which were requiring some fixes/formatting (total: %d)") % len(report))
        column_names = [trn("Filename"), trn("Fixed"), trn("Formatted <text>"), trn("Formatted")]
        table = create_table(column_names)

        for filename, fix, text_form, form in report:
            table.add_row(filename, fix, text_form, form)
            if fix == error_str or text_form == error_str or form == error_str:
                failed_files.append(filename)

        log.always(table_title)
        get_console().print(table)

        if len(failed_files) > 0:
            log.always(cf_cyan(trn("These files have syntax/other errors in them, so they weren't formatted.")))
            for file in failed_files:
                log.always("\t%s" % cf_yellow(file))
            log.always(cf_cyan(trn("Run command with --fix option to try to fix errors automatically\n")))
