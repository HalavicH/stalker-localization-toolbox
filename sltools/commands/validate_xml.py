from colorama import Fore
from lxml.etree import XMLSyntaxError

from sltools.commands.common import get_xml_files_and_log, process_files_with_progress
from sltools.utils.colorize import cf_green
from sltools.utils.file_utils import read_xml
from sltools.utils.xml_utils import *
from sltools.utils.lang_utils import _tr

include_example = cf_red(_tr('#include "some/other/file.xml"'))


def process_file(file_path, results, args):
    issues = []

    # 1. Test encoding
    try:
        with open(file_path, 'r', encoding=PRIMARY_ENCODING) as file:
            file.read()
    except UnicodeDecodeError as e:
        msg = _tr("Can't open file %s as %s encoded. Error: %s") % (file_path, PRIMARY_ENCODING, interpret_error(e))
        log.warning(msg)
        results.append((file_path, issues))
        return

    xml_string = read_xml(file_path)

    # 2. Check declaration
    try:
        xml_no_decl, declaration_correct = remove_xml_declaration(xml_string, file_path, log_and_save_err=False)
        if not declaration_correct:
            msg = _tr("The XML declaration is incorrect")
            issues.append(msg)
    except XMLSyntaxError as e:
        is_fatal, msg = analyze_xml_parser_error(e)
        issues.append(msg)
        if is_fatal:
            results.append((file_path, issues))
            return
    except ValueError as e:
        # Invalid declaration
        issues.append(str(e))
    except EmptyXmlDocError:
        issues.append(_tr("XML document is empty"))

    # 3. Check and resolve #include
    # TODO: handle error messages if they are in included content.
    if is_include_present(xml_string):
        msg = _tr('The document has %s-like macro which is not recommended. Try to resolve') % include_example
        issues.append(msg)

        try:
            xml_string = resolve_xml_includes(xml_string)
        except FileNotFoundError as e:
            msg = cf_red(interpret_error(e))
            issues.append(msg)

    # 4. Parse root
    try:
        root = parse_xml_root(xml_string.encode(PRIMARY_ENCODING))
    except Exception as e:
        is_fatal, msg = analyze_xml_parser_error(e, file_path, xml_string)
        issues.append(msg)
        if is_fatal:
            results.append((file_path, issues))
            return

    # 5. Validate against schema

    # 6. Validate against illegal characters

    # Finally
    if len(issues) > 0:
        results.append((file_path, issues))


def validate_xml(args, is_read_only):
    files = get_xml_files_and_log(args.paths, _tr("Validating XML-schema for"))

    results = []
    process_files_with_progress(files, process_file, results, args, is_read_only)

    log.info(_tr("Total processed files: %d") % len(files))
    display_report(results)


def display_report(report):
    if len(report) == 0:
        log.always(cf_green(_tr("All files are valid. Congrats")))
        return

    sorted_results = sorted(report, key=lambda x: x[0])

    log.always(('#' * 100))
    log.always(cf_red(_tr('\t\t\t\t\t Found %d invalid files:')) % len(report))
    log.always(('#' * 100))

    for file, issues in sorted_results:
        log.always((_tr('File: %s')) % cf_green(file))
        log.always(cf_yellow(_tr('Issues:')))
        for issue in issues:
            log.always(cf_yellow(f'\t{issue}'))
