from sltools.baseline.command_baseline import AbstractCommand
from sltools.baseline.config import PRIMARY_ENCODING
from sltools.log_config_loader import log
from sltools.root_commands.ValidateEncoding import ValidateEncoding
from sltools.utils.colorize import cf_green, cf_red, cf_yellow, cf_cyan
from sltools.utils.error_utils import log_and_save_error, display_encoding_error_details
from sltools.utils.file_utils import read_xml
from sltools.utils.lang_utils import trn


def change_file_encoding(file_name, e_from, e_to):
    with open(file_name, 'r', encoding=e_from) as file:
        data = file.read()

    try:
        with open(file_name, 'w', encoding=e_to) as file:
            file.write(data)
    except UnicodeEncodeError as e:
        # Rollback
        log.warning(trn("Can't change encoding for %s. Rolling back...") % file_name)
        with open(file_name, 'w', encoding=e_from) as file:
            file.write(data)
        # Rethrow
        raise e


class FixEncoding(AbstractCommand):
    # Metadata
    ##########
    def get_name(self) -> str:
        return "fix-encoding"

    def get_aliases(self) -> list:
        return ['fe']

    def _get_help(self) -> str:
        return trn('Fix UTF-8 encoding of a file or directory (Warning: may break encoding if detected wrongly)')

    def _setup_parser_args(self, parser):
        parser.add_argument('paths', nargs='*', help=trn('Paths to files or directories'))
        self._add_git_override_arguments(parser)

    # Execution
    ###########
    def _process_file(self, file_path, results: dict, args):
        file_name = file_path
        encoding = args.custom[file_path]

        if encoding.lower() == "utf-8":
            if not self.is_allowed_to_continue(file_name, args):
                return

            log.always(trn("Try to change encoding from %s to %s for file %s") % (cf_red(encoding), cf_green(PRIMARY_ENCODING), cf_cyan(file_name)))
            try:
                change_file_encoding(file_name, e_from=encoding, e_to=PRIMARY_ENCODING)
                log.always(cf_green(trn("Success!")))
                results["total_processed"] += 1
            except (UnicodeEncodeError, UnicodeDecodeError) as e:
                log_and_save_error(file_name, trn("Can't encode from %s to %s") % (cf_yellow(encoding), cf_yellow(PRIMARY_ENCODING)))
                display_encoding_error_details(read_xml(file_name, encoding), str(e))
        else:
            log.debug(trn("File %s possibly has %s encoding. But I'm not sure, so I won't do anything") % (file_name, encoding))

    def execute(self, args) -> dict:
        validation_results = ValidateEncoding().execute(args)
        log.always("")
        log.always(trn("All files analyzed! Fixing encodings..."))

        log.always(cf_yellow(trn("NOTE! Currently, reliable detection is only available for UTF-8 encoding.")))
        log.always(trn("For other suspicious files, manual review and encoding correction may be necessary."))

        supported_results = list(filter(lambda t: t[1].lower() == 'utf-8', validation_results["report"]))
        if len(supported_results) == 0:
            log.always(trn("Nothing to fix"))
            return {}

        log.always(cf_green(trn("There is/are %d file(s) to fix") % len(supported_results)))

        results = {"total_processed": 0}
        args.custom = {}
        for file, encoding, comment in supported_results:
            args.custom[file] = encoding

        self.process_files_with_progressbar(args, list(args.custom.keys()), results, False)

        log.info(trn("Files with fixed encoding: %d") % results["total_processed"])
        return results

    # Displaying
    ############
    def display_result(self, result: dict):
        pass
