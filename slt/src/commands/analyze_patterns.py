import json
import subprocess
import time
from collections import defaultdict
from datetime import datetime

import rich
from rich import pretty
from rich.panel import Panel

from src.commands.common import get_xml_files_and_log, process_files_with_progress
from src.log_config_loader import log
from src.utils.colorize import *
from src.utils.file_utils import read_xml
from src.utils.plain_text_utils import check_placeholders, analyze_patterns_in_text
from src.utils.xml_utils import parse_xml_root

# Dictionary keys
META_DATA_KEY = "meta_data"
SUMMARY_KEY = "summary"
PER_FILE_KEY = "per_file"
PER_STRING_KEY = "per_string"
FILENAME_KEY = "file_name"
PATTERNS_KEY = "patterns"
STRING_ID_KEY = "string_id"
NEWLINE_PATTERN = "\\n"
STRING_PATTERNS = "patterns"
PATTERN_ERRORS_KEY = "errors"


failed_files = {}
CURRENT_FILE_ISSUES = []


def serialize_analysis(analysis, file_path):
    with open(file_path, 'w') as file:
        json.dump(analysis, file, indent=4)


def deserialize_analysis(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def build_file_name():
    timestamp = int(time.time())
    try:
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], text=True).strip().replace('/',
                                                                                                                  '-').replace(
            ' ', '_')
        commit_name = subprocess.check_output(['git', 'log', '-1', '--pretty=format:%s'], text=True).strip().replace(
            ' ', '_').replace('/', '-').replace(':', '-')
        commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], text=True).strip()
        file_name = f'pattern-analysis_br-{branch}_cmt-{commit_name}_hash-{commit_hash}_time-{timestamp}.txt'
    except subprocess.CalledProcessError:
        file_name = f'pattern-analysis_{timestamp}.txt'
    return file_name


def process_file(file_path, per_file_results, args):
    xml_string = read_xml(file_path)
    root = parse_xml_root(xml_string)

    per_string_analysis = {}
    for string_tag in root.findall('.//string'):
        string_analysis = {
            STRING_PATTERNS: None,
            PATTERN_ERRORS_KEY: None
        }
        string_id = string_tag.get('id')
        text_tag = string_tag.find('text')
        if text_tag is not None:
            text_content = text_tag.text if text_tag.text else ''
            string_analysis[STRING_PATTERNS] = analyze_patterns_in_text(text_content)
            string_analysis[PATTERN_ERRORS_KEY] = check_placeholders(text_content)
            per_string_analysis[string_id] = string_analysis

    # file_patterns_summary, file_patterns_errors = sum_strings_to_file_analysis(per_string_analysis)
    file_patterns_summary, file_patterns_errors = aggregate_data(per_string_analysis)

    per_file_results[file_path] = {
        FILENAME_KEY: file_path,
        PATTERNS_KEY: file_patterns_summary,
        PATTERN_ERRORS_KEY: file_patterns_errors,
        PER_STRING_KEY: per_string_analysis
    }


def sum_strings_to_file_analysis(per_string_analysis):
    file_patterns_dict = {}
    file_patterns_errors = {}
    for string_name, string_report in per_string_analysis.items():
        for pattern_type, patterns_stats in string_report[PATTERNS_KEY].items():
            file_patterns_dict[pattern_type] = {}
            for pattern, cnt in patterns_stats.items():
                if file_patterns_dict[pattern_type][pattern] is not None:
                    file_patterns_dict[pattern_type][pattern] += cnt
                else:
                    file_patterns_dict[pattern_type][pattern] = cnt

        string_errors = string_report[PATTERN_ERRORS_KEY]
        if len(string_errors) > 0:
            file_patterns_errors[string_name] = string_errors

    return file_patterns_dict, file_patterns_errors


def aggregate_data(detailed_analysis):
    sum_pattens = {}
    sum_errors = {}
    for name, report in detailed_analysis.items():
        for pattern_type, patterns_stats in report[PATTERNS_KEY].items():
            sum_pattens[pattern_type] = {}
            for pattern, cnt in patterns_stats.items():
                if sum_pattens[pattern_type].get(pattern) is not None:
                    sum_pattens[pattern_type][pattern] += cnt
                else:
                    sum_pattens[pattern_type][pattern] = cnt


        string_errors = report[PATTERN_ERRORS_KEY]
        if len(string_errors) > 0:
            sum_errors[name] = string_errors

    return sum_pattens, sum_errors


def add_summary(current_analysis):
    file_analysis = current_analysis.pop(PER_FILE_KEY)

    current_analysis[SUMMARY_KEY] = {}

    summary = {}
    summary_pattens, summary_errors = aggregate_data(file_analysis)

    summary[PATTERNS_KEY] = summary_pattens
    summary[PATTERN_ERRORS_KEY] = summary_errors
    current_analysis[SUMMARY_KEY] = summary
    current_analysis[PER_FILE_KEY] = file_analysis
    return current_analysis


def add_meta_data(current_analysis):
    try:
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], text=True).strip().replace('/',
                                                                                                                  '-').replace(
            ' ', '_')
        commit_name = subprocess.check_output(['git', 'log', '-1', '--pretty=format:%s'], text=True).strip().replace(
            ' ', '_').replace('/', '-')
        commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
        git_info = {
            "branch": branch,
            "commit_name": commit_name,
            "commit_hash": commit_hash
        }
    except subprocess.CalledProcessError:
        git_info = "Unavailable"

    current_analysis[META_DATA_KEY] = {
        "git-info": git_info,
        "time-generated": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    }

    return current_analysis


def analyze_patterns(args):
    files = get_xml_files_and_log(args.paths, "Analyzing patterns for")

    results = {}
    results = add_meta_data(results)
    per_file_results = {}
    results[PER_FILE_KEY] = per_file_results

    process_files_with_progress(files, process_file, per_file_results, args)
    results = add_summary(results)

    log.info(f"Total processed files: {len(files)}")

    # Serialize the current analysis to a file
    serialize_analysis(results, build_file_name())

    display_report(results)

    # if args.compare_to_path is not None:
        # log.always(cf_cyan("Comparing previous analysis to freshly-generated"))
        # previous_analysis = deserialize_analysis(args.compare_to_path)
        # compare_analyses(previous_analysis, results)


# TODO: Add broken pattern analysis
def display_report(results):
    log.always("Displaying report")
    log.always("Summary:")

    patterns_report = results[SUMMARY_KEY][PATTERNS_KEY]
    errors = results[SUMMARY_KEY][PATTERN_ERRORS_KEY]
    log.always(f"Patterns:")
    for pattern_type, patterns in patterns_report.items():
        log.always(f"\t{cf_yellow(pattern_type)}:")
        for pattern, cnt in patterns.items():
            log.always(f"\t\t{cf_green(pattern)}: {cf_cyan(cnt)}")

    log.always(cf_red("#" * 80))
    log.always(cf_red(f"Errors:"))
    log.always(cf_red("#" * 80))
    for filename, file_report in errors.items():
        log.always(f"In file: {cf_yellow(filename)}:")

        for string, string_report in file_report.items():
            log.always(f"\tIn string with id: '{cf_green(string)}'")

            for error in string_report:
                row = error['position']['row']
                col = error['position']['column']
                cause = error['type']
                snippet = error['snippet']

                log.always(cf_red(f"\t\tError:"))
                log.always(f"\t\t\tCause: {cf_cyan(cause)}\n")
                log.always(f"\t\t\t'{snippet}'")
                log.always(f"\t\t\tRow: {cf_green(row)}, column {cf_green(col)}:")

    # rich.print(errors)
    log.always("Meta-data:")
    pretty.pprint(results[META_DATA_KEY])


def compare_analyses(previous_analysis, current_analysis, PATTERNS):
    mismatched_files = []
    total_patterns_prev = {}
    for pattern in PATTERNS:
        total_patterns_prev[pattern] = 0

    total_patterns_curr = dict(total_patterns_prev)  # Deep copy
    total_patterns_change = dict(total_patterns_prev)  # Deep copy

    # Get all file names from both the previous and current analyses
    previous_file_names = set(file[FILENAME_KEY] for file in previous_analysis[PER_FILE_KEY])
    current_file_names = set(file[FILENAME_KEY] for file in current_analysis[PER_FILE_KEY])

    # Check for missing or extra files in the current analysis
    missing_files = previous_file_names - current_file_names
    extra_files = current_file_names - previous_file_names
    if missing_files:
        print(f"Missing files in current analysis: {', '.join(missing_files)}")
    if extra_files:
        print(f"Extra files in current analysis: {', '.join(extra_files)}")

    # Only compare files that are present in both analyses
    common_files = previous_file_names.intersection(current_file_names)

    for file_name in common_files:
        # Fetch file analysis data by file name
        previous_file_data = next(file for file in previous_analysis[PER_FILE_KEY] if file[FILENAME_KEY] == file_name)
        current_file_data = next(file for file in current_analysis[PER_FILE_KEY] if file[FILENAME_KEY] == file_name)

        file_mismatched_patterns = {}
        for pattern in PATTERNS:
            prev_count = previous_file_data[PATTERNS_KEY].get(pattern, 0)
            total_patterns_prev[pattern] += prev_count

            curr_count = current_file_data[PATTERNS_KEY].get(pattern, 0)
            total_patterns_curr[pattern] += curr_count
            if prev_count != curr_count:
                change = curr_count - prev_count
                total_patterns_change[pattern] += change
                file_mismatched_patterns[pattern] = (prev_count, curr_count, change)

        per_text_tag_mismatched_patterns = {}
        # Ensure that we are comparing the same string tags within the file
        common_string_ids = set(previous_file_data[PER_STRING_KEY].keys()).intersection(
            set(current_file_data[PER_STRING_KEY].keys())
        )
        for string_id in common_string_ids:
            previous_tag_patterns = previous_file_data[PER_STRING_KEY][string_id]
            current_tag_patterns = current_file_data[PER_STRING_KEY][string_id]
            for pattern in PATTERNS:
                prev_count = previous_tag_patterns.get(pattern, 0)
                curr_count = current_tag_patterns.get(pattern, 0)
                if prev_count != curr_count:
                    change = curr_count - prev_count
                    per_text_tag_mismatched_patterns.setdefault(string_id, {})[pattern] = (
                        prev_count, curr_count, change)

        if file_mismatched_patterns or per_text_tag_mismatched_patterns:
            mismatched_files.append((file_name, file_mismatched_patterns, per_text_tag_mismatched_patterns))

    if mismatched_files:
        log.always(cf_yellow("#" * 80))
        log.always(cf_yellow(" " * 25 + "Mismatch in reports detected!"))
        log.always(cf_yellow("#" * 80))
        log.always(cf_blue("#" * 10 + " Total missmatch: " + "#" * 10))
        for pattern in PATTERNS:
            prev_count = total_patterns_prev[pattern]
            curr_count = total_patterns_curr[pattern]
            change = total_patterns_change[pattern]
            if change == 0:
                continue

            log.always(
                cf_blue(
                    f"Pattern: '{pattern}', {abs(change)} {'more' if change > 0 else 'less'} than before. Before {prev_count} after {curr_count}"))

        log.always(cf_magenta("\t" + "#" * 10 + " Mismatched files: " + "#" * 10))
        for file, file_mismatches, text_tag_mismatches in mismatched_files:
            log.always(cf_magenta(f"\nFile: '{file}'"))
            for pattern, counts in file_mismatches.items():
                prev_count, curr_count, change = counts
                log.always(
                    cf_magenta(
                        f"\tPattern: '{pattern}', {abs(change)} {'more' if change > 0 else 'less'} than before. Before {prev_count} after {curr_count}"))
            log.always(cf_green("\t" + "#" * 10 + " Mismatched strings: " + "#" * 10))
            for string_id, tag_mismatches in text_tag_mismatches.items():
                log.always(cf_green(f"\tstring: '{string_id}'"))
                for pattern, counts in tag_mismatches.items():
                    prev_count, curr_count, change = counts
                    log.always(
                        cf_green(
                            f"\t\tPattern: '{pattern}', {abs(change)} {'more' if change > 0 else 'less'} than before. Before {prev_count} after {curr_count}"))
    else:
        log.always(cf_green("#" * 30))
        log.always(cf_green("Versions match! Jolly good!"))
        log.always(cf_green("#" * 30))
