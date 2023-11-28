from argparse import Namespace

from rich import get_console

from sltools.baseline.command_baseline import AbstractCommand
from sltools.log_config_loader import log
from sltools.baseline.common import get_xml_files_and_log
from sltools.utils.colorize import cf_green, cf_red
from sltools.utils.encoding_utils import detect_encoding, is_file_content_win1251_compatible
from sltools.utils.lang_utils import trn
from sltools.utils.misc import create_table


class ValidateEncoding(AbstractCommand):
    # Metadata
    ##########
    def get_name(self) -> str:
        return "validate-encoding"

    def get_aliases(self) -> list:
        return ['ve']

    def _get_help(self) -> str:
        return trn('Validate encoding of a file or directory')

    def _setup_parser_args(self, parser):
        parser.add_argument('paths', nargs='*', help=trn('Paths to files or directories'))

    # Execution
    ###########
    def _process_file(self, file_path, results: dict, args):
        with open(file_path, 'rb') as f:
            binary_text = f.read()

        encoding = detect_encoding(binary_text)
        compatible, comment = is_file_content_win1251_compatible(binary_text, encoding)
        if compatible:
            log.debug(trn("File %s is ok. Encoding: %s") % (file_path, encoding))
            return

        results["report"].append((file_path, encoding, comment))

    def execute(self, args: Namespace) -> dict:
        files = get_xml_files_and_log(args.paths, trn("Validating encoding for"))

        results = {"report": []}
        self.process_files_with_progressbar(args, files, results, True)

        log.info(trn("Total processed files: %d") % len(files))
        return results

    # Displaying
    ############
    def display_result(self, result: dict):
        report = result["report"]

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
