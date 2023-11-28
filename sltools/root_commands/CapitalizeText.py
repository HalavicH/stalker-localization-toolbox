from rich import get_console

from sltools.baseline.command_baseline import AbstractCommand
from sltools.log_config_loader import log
from sltools.baseline.common import get_xml_files_and_log
from sltools.utils.colorize import cf_cyan
from sltools.utils.file_utils import read_xml, save_xml
from sltools.utils.lang_utils import trn
from sltools.utils.misc import create_table
from sltools.utils.xml_utils import format_xml_string, parse_xml_root, to_utf_string_with_proper_declaration


class CapitalizeText(AbstractCommand):
    # Metadata
    ##########
    def get_name(self) -> str:
        return "capitalize-text-entries"

    def get_aliases(self) -> list:
        return ['cte']

    def _get_help(self) -> str:
        return trn('Capitalize first letter [cyan](a->A)[/cyan] in all text entries in a file or directory')

    def _setup_parser_args(self, parser):
        parser.add_argument('paths', nargs='*', help=trn('Paths to files or directories'))
        self._add_git_override_arguments(parser)

    # Execution
    ###########
    def _process_file(self, file_path, results: dict, args):
        report = results["report"]
        counter = 0
        xml_string = read_xml(file_path)
        root = parse_xml_root(xml_string)

        for string_elem in root:
            for text_elem in string_elem:
                orig_text = text_elem.text
                text_elem.text = self._capitalize_first_letter(orig_text)
                if orig_text != text_elem.text:
                    str_id = cf_cyan(string_elem.attrib.get("id"))
                    log.info(trn("Text of '%s' was capitalized") % str_id)
                    counter += 1

        resulting_xtr = to_utf_string_with_proper_declaration(root)
        formatted_xml_str = format_xml_string(resulting_xtr, file_path)
        save_xml(file_path, formatted_xml_str)

        if counter > 0:
            report.append((file_path, counter))

    @staticmethod
    def _capitalize_first_letter(s):
        for index, char in enumerate(s):
            if char.isalpha():  # Check if the character is alphabetic
                return s[:index] + char.upper() + s[index + 1:]  # Capitalize and return
            elif char != ' ' and char != '\n':  # If the character is not a space and not alphabetic, return original string
                return s
        return s  # Return original string if no alphabetic characters are found

    def execute(self, args) -> dict:
        files = get_xml_files_and_log(args.paths, trn("Analyzing patterns for"))

        results = {"report": []}
        self.process_files_with_progressbar(args, files, results, False)

        return results

    # Displaying
    ############
    def display_result(self, result: dict):
        report = result["report"]
        if len(report) == 0:
            log.always(trn("No files were modified"))

        table = create_table([trn("File"), trn("Cnt")])

        for file, cnt in report:
            table.add_row(file, str(cnt))

        log.always(trn("Capitalized text blocks per file. Total files modified: %d") % len(report))
        get_console().print(table)
