import sys

from rich import get_console

from src.commands.common import get_xml_files_and_log, process_files_with_progress
from src.log_config_loader import log
from src.utils.file_utils import read_xml
from src.utils.misc import create_table
from src.utils.xml_utils import parse_xml_root


def process_file(file_path, results, args):
    xml_string = read_xml(file_path)
    root = parse_xml_root(xml_string)

    for string_elem in root.findall(".//string"):
        string_id = string_elem.get("id")
        text_elem = string_elem.find("text")
        text_content = text_elem.text.strip() if text_elem is not None else ""

        line_num = xml_string.count('\n', 0, xml_string.find(string_id)) + 1

        data_obj = {
            "file_path": file_path,
            "text": text_content,
            "line": line_num
        }

        if string_id in results:
            log.warning(f"Found duplicate of '{string_id}' in '{file_path}'")
            results[string_id].append(data_obj)
        else:
            results[string_id] = [data_obj]


def display_report(results):
    if len(results) == 0:
        log.always("No duplicates found! Great news")

    # table = create_table(["String", "Cnt"])
    #
    # for file, cnt in results:
    #     table.add_row(file, str(cnt))
    #
    # log.always(f"Following duplicated strings were found: {len(results)}")
    # get_console().print(table)

    # Print duplicate counts
    for string_id, data_list in results.items():
        if len(data_list) > 1:
            print(f"{string_id}: {len(data_list)} duplicates")

    # Print memory footprint
    memory_size = sys.getsizeof(results)
    for data_list in results.values():
        memory_size += sum(sys.getsizeof(i) for i in data_list)
    print(f"\nMemory footprint of the dictionary: {memory_size / 1024:.2f} KB")


def find_string_duplicates(args, is_read_only):
    files = get_xml_files_and_log(args.paths, "Analyzing patterns for")

    results = {}

    process_files_with_progress(files, process_file, results, args, is_read_only)
    log.info(f"Total processed files: {len(files)}")

    display_report(results)
