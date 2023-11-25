from rich import get_console

from sltools.baseline.command_baseline import AbstractCommand
from sltools.log_config_loader import log
from sltools.old.commands.format_xml import error_str, format_xml_text_entries, to_yes_no
from sltools.old.commands.utils.common import get_xml_files_and_log
from sltools.utils.colorize import cf_green, cf_red, cf_yellow, cf_cyan
from sltools.utils.error_utils import log_and_save_error
from sltools.utils.file_utils import read_xml, save_xml
from sltools.utils.lang_utils import trn
from sltools.utils.misc import create_table, exception_originates_from
from sltools.utils.plain_text_utils import tabwidth, format_text_entry
from sltools.utils.xml_utils import fix_possible_errors, format_xml_string, parse_xml_root, indent, to_utf_string_with_proper_declaration, \
    add_blank_line_before_comments


class FormatXml(AbstractCommand):
    # Metadata
    ##########
    def get_name(self) -> str:
        return "format-xml"

    def get_aliases(self) -> list:
        return ['fx']

    def _get_help(self) -> str:
        return trn('Format XML of a file or directory')

    def _setup_parser_args(self, parser):
        parser.add_argument('paths', nargs='*', help=trn('Paths to files or directories'))
        parser.add_argument('--fix', action='store_true',
                            help=trn('Fix XML issues if possible instead of skipping the file'))
        parser.add_argument('--format-text-entries', action='store_true',
                            help=trn('Format <text> tag contents to resemble in-game appearance'))
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
        apply_fix = args.fix
        format_text_entries = args.format_text_entries

        if apply_fix:
            log.always(cf_cyan(trn("Fix option enabled. Will fix:") +
                               trn("\n\t- Guard '--' in comments,") +
                               trn("\n\t- Ampersand misuse (& -> &amp;),") +
                               trn("\n\t- Resolve #include") +
                               trn("\n\t- Wrong/missing XML declaration")))

        if format_text_entries:
            log.always(cf_cyan(trn("Format <text> content option enabled. Will make text look as similar as possible to the in-game text")))

        files = get_xml_files_and_log(args.paths, trn("Formatting XML-schema for"))

        results = {"report": []}
        self.process_files_with_progressbar(args, files, results, False)

        return results

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

