import json
import sys
from collections import defaultdict

from rich import get_console

from src.commands.common import get_xml_files_and_log, process_files_with_progress
from src.log_config_loader import log
from src.utils.colorize import cf_yellow, cf_cyan
from src.utils.file_utils import read_xml
from src.utils.flask_server import run_flask_server
from src.utils.misc import create_table
from src.utils.xml_utils import parse_xml_root


def process_file(file_path, results, args):
    strings_element_list, xml_string = list_strings(file_path)
    for string_elem in strings_element_list:
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


def list_strings_from_all_files(files):
    results = {}

    for file in files:
        xml_string_tags, _ = list_strings(file)
        strings = []
        for string_tag in xml_string_tags:
            strings.append(string_tag.get("id"))
        results[file] = strings

    return results


def list_strings(file_path):
    xml_string = read_xml(file_path)
    root = parse_xml_root(xml_string)
    strings_element_list = root.findall(".//string")
    return strings_element_list, xml_string


def display_per_string(results):
    if len(results) == 0:
        log.always("No duplicates found! Great news")

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

    # Print memory footprint
    memory_size = sys.getsizeof(results)
    for data_list in results.values():
        memory_size += sum(sys.getsizeof(i) for i in data_list)
    print(f"\nMemory footprint of the dictionary: {memory_size / 1024:.2f} KB")


def init_file_overlaps_dict():
    return defaultdict(lambda:
                       {
                           "overlaps": defaultdict(lambda: defaultdict(
                               lambda: {'match_count': 0, 'overlapping_ids': set(), 'total_id_cnt': 0})),
                           "total_id_cnt": 0
                       })


def sort_overlaps(data_dict: defaultdict) -> dict:
    # Sort the inner overlaps by match_count
    for file, data in data_dict.items():
        data["overlaps"] = dict(sorted(data["overlaps"].items(), key=lambda x: x[1]["match_count"], reverse=True))

    # Sort the main dictionary by the total match_count of its overlaps
    sorted_data_dict = dict(
        sorted(data_dict.items(), key=lambda x: sum([y["match_count"] for y in x[1]["overlaps"].values()]),
               reverse=True))

    return sorted_data_dict


def filter_sorted_data(sorted_data_dict: dict) -> dict:
    # Filter out main entries with empty overlaps
    filtered_data_dict = {k: v for k, v in sorted_data_dict.items() if v['overlaps']}
    return filtered_data_dict


def analyze_file_overlaps(indexed_data):
    # Create a dictionary to hold unique string IDs for each file
    file_string_ids = defaultdict(set)

    for string_id, data_list in indexed_data.items():
        for entry in data_list:
            file_string_ids[entry['file_path']].add(string_id)

    # Compare each file's string IDs with every other file's string IDs
    overlaps_data = init_file_overlaps_dict()
    files = list(file_string_ids.keys())
    for i, file1 in enumerate(files):
        overlaps_data[file1]["total_id_cnt"] = len(file_string_ids[file1])

        for j, file2 in enumerate(files):
            if i != j:
                overlapping_ids = file_string_ids[file1].intersection(file_string_ids[file2])
                overlap_count = len(overlapping_ids)
                if overlap_count > 0:
                    overlaps_data[file1]["overlaps"][file2]["total_id_cnt"] = len(file_string_ids[file2])
                    overlaps_data[file1]["overlaps"][file2]['match_count'] = overlap_count
                    overlaps_data[file1]["overlaps"][file2]['overlapping_ids'] = overlapping_ids

    # Sort the overlaps
    sorted_overlaps = sort_overlaps(overlaps_data)
    return filter_sorted_data(sorted_overlaps)


def display_per_file_overlaps(overlaps, show_unique=False):
    # Print the analysis
    for i, (file, matched_files) in enumerate(overlaps.items()):
        main_file_ids_cnt = matched_files["total_id_cnt"]

        log.always(f"Duplicates in files:")
        log.always(f"file #{i + 1}: {file} (Total IDs: {main_file_ids_cnt}):")

        for matched_file, data in matched_files["overlaps"].items():
            file_ids_cnt = data['total_id_cnt']
            percentage_match = (data['match_count'] / file_ids_cnt) * 100
            log.always(
                f"file: '{matched_file}', overlapping IDs: {cf_yellow(data['match_count'])}/[cyan]{file_ids_cnt} [bright_black]({percentage_match:.2f}%)[/bright_black]")

            overlapping_ids = "\n\t".join(list(data['overlapping_ids']))
            log.always(f"Overlapping ids:\n\t{cf_yellow(overlapping_ids)}")

            if show_unique:
                unique_ids = set(data['overlapping_ids']) - set(overlaps[matched_file].keys())
                unique_ids_str = "\n\t".join(list(unique_ids))
                log.always(f"Unique ids in {file} (not in {matched_file}):\n\t{cf_yellow(unique_ids_str)}")

        log.always()


def find_string_duplicates(args, is_read_only):
    files = get_xml_files_and_log(args.paths, "Analyzing patterns for")

    results = {}

    process_files_with_progress(files, process_file, results, args, is_read_only)
    log.info(f"Total processed files: {len(files)}")

    if args.per_string_report:
        display_per_string(results)
    else:
        overlaps = analyze_file_overlaps(results)
        visualization_data = {
            "overlaps_report": overlaps,
            "file_to_string_mapping": list_strings_from_all_files(files)
        }

        # with open("visualization_data.json", 'w', encoding='utf-8') as f:
        #     json.dump(visualization_data, f, default=set_default, ensure_ascii=False, indent=4)

        if args.web_visualizer:
            run_flask_server(visualization_data)

        display_per_file_overlaps(overlaps)
