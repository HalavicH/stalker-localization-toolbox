from lxml.etree import XMLSyntaxError

from sltools.baseline.command_baseline import AbstractCommand
from sltools.log_config_loader import log
from sltools.baseline.common import get_xml_files_and_log
from sltools.baseline.config import PRIMARY_ENCODING
from sltools.utils.colorize import cf_green, cf_red, cf_yellow
from sltools.utils.error_utils import interpret_error
from sltools.utils.file_utils import read_xml
from sltools.utils.lang_utils import trn
from sltools.utils.xml_utils import remove_xml_declaration, analyze_xml_parser_error, EmptyXmlDocError, is_include_present, resolve_xml_includes, parse_xml_root


include_example = cf_red(trn('#include "some/other/file.xml"'))

class ValidateXml(AbstractCommand):
    # Metadata
    ##########
    def get_name(self) -> str:
        return "validate-xml"

    def get_aliases(self) -> list:
        return ['vx']

    def _get_help(self) -> str:
        return trn('Validate XML of a file or directory')

    def _setup_parser_args(self, parser):
        parser.add_argument('paths', nargs='*', help=trn('Paths to files or directories'))

    # Execution
    ###########
    def _process_file(self, file_path, results: dict, args):
        issues = []
        report = results["report"]

        # 1. Test encoding
        try:
            with open(file_path, 'r', encoding=PRIMARY_ENCODING) as file:
                file.read()
        except UnicodeDecodeError as e:
            msg = trn("Can't open file %s as %s encoded. Error: %s") % (file_path, PRIMARY_ENCODING, interpret_error(e))
            log.warning(msg)
            report.append((file_path, issues))
            return

        xml_string = read_xml(file_path)

        # 2. Check declaration
        try:
            xml_no_decl, declaration_correct = remove_xml_declaration(xml_string, file_path, log_and_save_err=False)
            if not declaration_correct:
                msg = trn("The XML declaration is incorrect")
                issues.append(msg)
        except XMLSyntaxError as e:
            is_fatal, msg = analyze_xml_parser_error(e)
            issues.append(msg)
            if is_fatal:
                report.append((file_path, issues))
                return
        except ValueError as e:
            # Invalid declaration
            issues.append(str(e))
        except EmptyXmlDocError:
            issues.append(trn("XML document is empty"))

        # 3. Check and resolve #include
        # TODO: handle error messages if they are in included content.
        if is_include_present(xml_string):
            msg = trn('The document has %s-like macro which is not recommended. Try to resolve') % include_example
            issues.append(msg)

            try:
                xml_string = resolve_xml_includes(xml_string)
            except FileNotFoundError as e:
                msg = cf_red(interpret_error(e))
                issues.append(msg)

        # 4. Parse root
        try:
            _ = parse_xml_root(xml_string.encode(PRIMARY_ENCODING))
        except Exception as e:
            is_fatal, msg = analyze_xml_parser_error(e, file_path, xml_string)
            issues.append(msg)
            if is_fatal:
                report.append((file_path, issues))
                return

        # 5. Validate against schema
        # TODO

        # 6. Validate against illegal characters

        # Finally
        if len(issues) > 0:
            report.append((file_path, issues))

    def execute(self, args) -> dict:
        files = get_xml_files_and_log(args.paths, trn("Validating XML-schema for"))

        result = {"report": []}
        self.process_files_with_progressbar(args, files, result, True)

        return result

    # Displaying
    ############
    def display_result(self, result: dict):
        report = result["report"]
        if len(report) == 0:
            log.always(cf_green(trn("All files are valid. Congrats")))
            return

        sorted_results = sorted(report, key=lambda x: x[0])

        log.always(('#' * 100))
        log.always(cf_red(trn('\t\t\t\t\t Found %d invalid files:')) % len(report))
        log.always(('#' * 100))

        for file, issues in sorted_results:
            log.always((trn('File: %s')) % cf_green(file))
            log.always(cf_yellow(trn('Issues:')))
            for issue in issues:
                log.always(cf_yellow(f'\t{issue}'))
