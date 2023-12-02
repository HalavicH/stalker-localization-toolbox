import json
import sys
from collections import defaultdict
from datetime import datetime

from sltools.baseline.command_baseline import AbstractCommand
from sltools.baseline.common import get_xml_files_and_log
from sltools.log_config_loader import log
from sltools.utils.colorize import cf_yellow, cf_cyan
from sltools.utils.error_utils import interpret_error
from sltools.utils.file_utils import read_xml
from sltools.web_server.flask_server import WebUiServer
from sltools.utils.lang_utils import trn
from sltools.utils.misc import set_default
from sltools.utils.xml_utils import parse_xml_root
from sltools.web_server.fsd_manager import FindStringDuplicatesManager


def list_strings_from_all_files(files):
    results = {}

    for file in files:
        try:
            xml_string_tags, _ = list_strings(file)
            strings = {}
            for string_tag in xml_string_tags:
                strings[string_tag.get("id")] = hash(string_tag.find("text").text.strip())
            results[file] = strings
        except Exception as e:
            log.error(trn("Can't get strings for file: '%s'. Error: %s") % (file, interpret_error(e)))

    return results


def list_strings(file_path):
    xml_string = read_xml(file_path)
    root = parse_xml_root(xml_string)
    strings_element_list = root.findall(".//string")
    return strings_element_list, xml_string


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


class FindStringDuplicates(AbstractCommand):
    # Metadata
    ##########
    def get_name(self) -> str:
        return "find-string-duplicates"

    def get_aliases(self) -> list:
        return ['fsd']

    def _get_help(self) -> str:
        return trn("Looks for duplicates of [green]'<string id=\"...\">'[/green] to eliminate unwanted conflicts. Provides filecentric report by default")

    def _setup_parser_args(self, parser):
        parser.add_argument('--per-string-report', action='store_true', default=False,
                            help=trn('Display detailed report with string text'))
        parser.add_argument('--web-visualizer', action='store_true', default=False,
                            help=trn('Display duplicates as D3 interactive graph'))
        parser.add_argument('--save-report', action='store_true', default=False,
                            help=trn('Save filecentric report as JSON'))
        parser.add_argument('paths', nargs='*', help=trn('Paths to files or directories'))

    # Execution
    ###########
    def _process_file(self, file_path, results: dict, args):
        try:
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
                    log.warning(trn("Found duplicate of '%s' in '%s'") % (string_id, file_path))
                    results[string_id].append(data_obj)
                else:
                    results[string_id] = [data_obj]
        except Exception as e:
            log.error(trn("Can't process strings for file: '%s'. Error: %s") % (file_path, interpret_error(e)))

    def find_and_prepare_duplicates_report(self, args):
        files = get_xml_files_and_log(args.paths, trn("Analyzing patterns for"))

        results = {}
        self.process_files_with_progressbar(args, files, results, True)
        overlaps = analyze_file_overlaps(results)
        visualization_data = {
            "overlaps_report": overlaps,
            "file_to_string_mapping": list_strings_from_all_files(files)
        }
        return results, visualization_data

    def execute(self, args) -> dict:
        def fsd_wrapper_for_ws(_args):
            return self.find_and_prepare_duplicates_report(_args)

        if args.web_visualizer:
            manager = FindStringDuplicatesManager(args, fsd_wrapper_for_ws)
            WebUiServer(manager).run()
            return {}

        report, visualization_data = self.find_and_prepare_duplicates_report(args)

        if args.save_report:
            timestamp = datetime.now()
            with open(trn("duplicates-report-%s.json") % timestamp, 'w', encoding='utf-8') as f:
                json.dump(visualization_data, f, default=set_default, ensure_ascii=False, indent=4)

        return {"report": report, "visualization_data": visualization_data, "per_string_report": args.per_string_report}

    # Displaying
    ############
    def display_result(self, result: dict):
        if result == {}:
            log.always(trn("Nothing to report"))
            return

        per_string_report = result["per_string_report"]
        report = result["report"]
        visualization_data = result["visualization_data"]
        if per_string_report:
            self.__display_per_string(report)
        else:
            self.__display_per_file_overlaps(visualization_data["overlaps_report"])

    @staticmethod
    def __display_per_string(results):
        if len(results) == 0:
            log.always(trn("No duplicates found! Great news"))

        # Print duplicate counts and details
        for string_id, data_list in results.items():
            if len(data_list) > 1:
                msg = trn("For string '%s' found %s duplicates:") % (string_id, len(data_list))
                len_msg = len(msg) * "#"
                log.always(cf_yellow(len_msg))
                log.always(msg)
                log.always(cf_yellow(len_msg))
                for i, candidate in enumerate(data_list, 1):
                    file_path = candidate['file_path']
                    line = candidate['line']
                    text = candidate['text']
                    log.always(cf_cyan(trn("Candidate #d:") % i))
                    log.always(trn("File: '%s', line: %s") % (file_path, line))
                    log.always(trn("Text: '%s'\n") % cf_yellow(text))

        # Print memory footprint
        memory_size = sys.getsizeof(results)
        for data_list in results.values():
            memory_size += sum(sys.getsizeof(i) for i in data_list)
        log.log(trn("\nMemory footprint of the report for the dictionary: %.2d KB") % (memory_size / 1024))

    @staticmethod
    def __display_per_file_overlaps(overlaps, show_unique=False):
        if len(overlaps) == 0:
            log.always(trn("No duplicates found"))
            return

        # Print the analysis
        for i, (file, matched_files) in enumerate(overlaps.items()):
            main_file_ids_cnt = matched_files["total_id_cnt"]

            log.always(trn("Duplicates in files:"))
            log.always(trn("file #%d: %s (Total IDs: %d):") % (i + 1, file, main_file_ids_cnt))

            for matched_file, data in matched_files["overlaps"].items():
                file_ids_cnt = data['total_id_cnt']
                percentage_match = (data['match_count'] / file_ids_cnt) * 100
                log.always(trn("file: '%s', overlapping IDs: %s/%s (%.2f%%)") % (matched_file, cf_yellow(data['match_count']), file_ids_cnt, percentage_match))

                overlapping_ids = "\n\t".join(list(data['overlapping_ids']))
                log.always(trn("Overlapping ids:\n\t%s") % cf_yellow(overlapping_ids))

                if show_unique:
                    unique_ids = set(data['overlapping_ids']) - set(overlaps[matched_file].keys())
                    unique_ids_str = "\n\t".join(list(unique_ids))
                    log.always(trn("Unique ids in %s (not in %s):\n\t%s") % (file, matched_file, cf_yellow(unique_ids_str)))

                log.always()
