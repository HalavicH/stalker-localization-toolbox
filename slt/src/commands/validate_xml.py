import codecs
import time

from colorama import Fore
from lxml.etree import XMLSyntaxError
from rich.progress import Progress

from src.log_config_loader import log
from src.utils.colorize import cf_green, cf_red
from src.utils.file_utils import find_xml_files
from src.utils.misc import get_term_width
from src.utils.xml_utils import *

include_example = cf_red('#include "some/other/file.xml"')


def process_file(file_path, results):
    issues = []
    """
    Open file as win-1251
        on failure -> issue wrong encoding
    Try to load root
        on failure -> issue:
            no root
            multiple roots
    """
    # with codecs.open(file_path, 'r', encoding='windows-1251') as file:
    #     xml_string = file.read()
    # 1. Test encoding
    try:
        with open(file_path, 'r', encoding=windows_1251) as file:
            file.read()
    except UnicodeDecodeError as e:
        msg = f"Can't open file {file_path} as {windows_1251} encoded. Error: {e}"
        log.warning(msg)
        results.append((file_path, issues))
        return

    xml_string = read_xml(file_path)

    # 2. Check declaration
    try:
        xml_no_decl, declaration_correct = remove_xml_declaration(xml_string, file_path, log_and_save_err=False)
        if not declaration_correct:
            msg = "The XML declaration is incorrect"
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

    # 3. Check and resolve #include
    # TODO: handle error messages if they are in included content.
    if is_include_present(xml_string):
        msg = f'The document has {include_example + Fore.YELLOW}-like macro which is not recommended. Try to resolve'
        issues.append(msg)

        try:
            xml_string = resolve_xml_includes(xml_string)
        except FileNotFoundError as e:
            msg = cf_red(str(e).replace("[Errno 2] ", "\tError: Can't resolve include! "))
            issues.append(msg)

    # 4. Parse root
    try:
        root = parse_xml_root(xml_string.encode(windows_1251))
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


def validate_xml(args):
    files = find_xml_files(args.path)
    log.always(f"Validating XML-schema for {cf_green(len(files))} files")

    term_width = get_term_width()
    if term_width > 130:
        max_file_width = term_width - 80
    else:
        max_file_width = term_width - 60

    results = []
    with Progress() as progress:
        task = progress.add_task("Processing...", total=len(files))
        for i, file_path in enumerate(files):
            # Truncate the file_path path if it exceeds the maximum width
            truncated_file = (
                "..." + file_path[-(max_file_width - 5):]
                if len(file_path) > max_file_width
                else file_path.ljust(max_file_width)
            )

            # Update the progress bar with the truncated description
            progress.update(task, completed=i,
                            description=f"Processing file_path [green]#{i:03}[/] with name [green]{truncated_file}[/]")

            log.debug(f"Processing file #{i}")
            try:
                process_file(file_path, results)
            except Exception as e:
                log_and_save_error(file_path, f"Unhandled error {e}")
        log.info(f"Total processed files: {len(files)}")

    if len(results) > 0:
        print_report(results)
    else:
        log.always(cf_green("All files are valid. Congrats"))

    return results


def print_report(results):
    sorted_results = sorted(results, key=lambda x: x[0])

    log.always(('#' * 100))
    log.always(cf_red(f'\t\t\t\t\t Found {len(results)} invalid files:'))
    log.always(('#' * 100))

    for file, issues in sorted_results:
        log.always((f'File: {cf_green(file)}'))
        log.always(cf_yellow(f'Issues:'))
        for issue in issues:
            log.always(cf_yellow(f'\t{issue}'))
