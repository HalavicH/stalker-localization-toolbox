import sys
from collections import defaultdict

from rich import get_console

from src.commands.common import get_xml_files_and_log, process_files_with_progress
from src.log_config_loader import log
from src.utils.colorize import cf_yellow, cf_cyan
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

    # Print duplicate counts and details
    for string_id, data_list in results.items():
        if len(data_list) > 1:
            msg = f"For string '{string_id}' found {len(data_list)} duplicates:"
            log.always(cf_yellow(len(msg) * "#"))
            log.always(f"For string '{string_id}' found {len(data_list)} duplicates:")
            log.always(cf_yellow(len(msg) * "#"))
            for i, candidate in enumerate(data_list, 1):
                file_path = candidate['file_path']
                line = candidate['line']
                text = candidate['text']
                log.always(cf_cyan(f"Candidate #{i}:"))
                log.always(f"File: '{file_path}', line: {line}")
                log.always(f"Text: '{cf_yellow(text)}'\n")

    overlaps = analyze_file_overlaps(results)
    print_file_overlaps(overlaps)

    # Print memory footprint
    memory_size = sys.getsizeof(results)
    for data_list in results.values():
        memory_size += sum(sys.getsizeof(i) for i in data_list)
    print(f"\nMemory footprint of the dictionary: {memory_size / 1024:.2f} KB")


def analyze_file_overlaps(indexed_data):
    # Create a dictionary to hold unique string IDs for each file
    file_string_ids = defaultdict(set)

    for data_list in indexed_data.values():
        for entry in data_list:
            file_string_ids[entry['file_path']].add(entry['text'])

    # Compare each file's string IDs with every other file's string IDs
    overlaps = defaultdict(lambda: defaultdict(int))
    files = list(file_string_ids.keys())
    for i, file1 in enumerate(files):
        for j, file2 in enumerate(files):
            if i != j:
                overlap_count = len(file_string_ids[file1].intersection(file_string_ids[file2]))
                if overlap_count > 0:
                    overlaps[file1][file2] = overlap_count

    # Sort the overlaps
    sorted_overlaps = {file: dict(sorted(overlaps[file].items(), key=lambda item: item[1], reverse=True)) for file in
                       overlaps}

    return sorted_overlaps


def print_file_overlaps(overlaps):
    # Print the analysis
    for i, (file, matched_files) in enumerate(overlaps.items()):
        total_ids_in_file = sum(overlaps[file].values()) + len(overlaps[file])  # Total IDs in primary file
        log.always(f"Duplicates in files:")
        log.always(f"file #{i + 1}: {file} matches with:")
        for matched_file, count in matched_files.items():
            percentage_match = (count / total_ids_in_file) * 100
            log.always(
                f"file: '{matched_file}', overlapping IDs: {cf_yellow(count)}/[cyan]{total_ids_in_file} [bright_black]({percentage_match:.2f}%)[/bright_black]")
        log.always()

def find_string_duplicates(args, is_read_only):
    files = get_xml_files_and_log(args.paths, "Analyzing patterns for")

    results = {}

    process_files_with_progress(files, process_file, results, args, is_read_only)
    log.info(f"Total processed files: {len(files)}")

    display_report(results)
