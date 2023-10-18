"""
Script for analyzing and comparing pattern occurrences in XML files.

Dependencies:
- argparse
- xml.etree.ElementTree
- pprint
- datetime
- colorama

Install with:
pip3 install argparse xml datetime pprint colorama
"""

import glob
import json
import argparse
import subprocess
import time
import xml.etree.ElementTree as ET

import pprint as pp
from datetime import datetime

import colorama
from colorama import Fore

colorama.init(autoreset=True)

# Dictionary keys
META_DATA_KEY = "meta_data"
SUMMARY_KEY = "summary"
PER_FILE_KEY = "per_file"
PER_TEXT_TAG_KEY = "per_text_tag"
FILENAME_KEY = "file_name"
PATTERNS_KEY = "patterns"
STRING_ID_KEY = "string_id"
NEWLINE_PATTERN = "\\n"

PLACEHOLDER_S_PATTERN = "%s"
PLACEHOLDER_GRAY_PATTERN = "%c[ui_gray_2]"
PLACEHOLDER_LIGHT_GRAY_PATTERN = "%c[ui_gray_1]"
PLACEHOLDER_BLUE_PATTERN = "%c[d_cyan]"
PLACEHOLDER_ORANGE_PATTERN = "%c[d_orange]"
PLACEHOLDER_RED_PATTERN = "%c[d_red]"
PLACEHOLDER_PURPLE_PATTERN = "%c[d_purple]"
PLACEHOLDER_GREEN_PATTERN = "%c[d_green]"
PLACEHOLDER_YELLOW_PATTERN = "%c[0,250,250,0]"
PLACEHOLDER_WHITE_PATTERN = "%c[0,255,255,255]"

patterns = [
    NEWLINE_PATTERN,
    PLACEHOLDER_S_PATTERN,
    PLACEHOLDER_GRAY_PATTERN,
    PLACEHOLDER_LIGHT_GRAY_PATTERN,
    PLACEHOLDER_BLUE_PATTERN,
    PLACEHOLDER_ORANGE_PATTERN,
    PLACEHOLDER_RED_PATTERN,
    PLACEHOLDER_PURPLE_PATTERN,
    PLACEHOLDER_GREEN_PATTERN,
    PLACEHOLDER_YELLOW_PATTERN,
    PLACEHOLDER_WHITE_PATTERN
]

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


def analyze_patterns_in_text(text, patterns):
    return {pattern: text.count(pattern) for pattern in patterns}


def analyze_patterns_in_file(file_path, patterns):
    print(f"Analyzing file: {file_path}")
    with open(file_path, 'r', encoding='windows-1251', errors='ignore') as file:
        xml_content = file.read()
    tree = ET.ElementTree(ET.fromstring(xml_content))
    per_text_tag_analysis = {}
    for string_tag in tree.findall('.//string'):
        string_id = string_tag.get('id')
        text_tag = string_tag.find('text')
        if text_tag is not None:
            text_content = text_tag.text if text_tag.text else ''
            per_text_tag_analysis[string_id] = analyze_patterns_in_text(text_content, patterns)
    file_patterns_dict = {
        pattern: sum(tag_patterns.get(pattern, 0) for tag_patterns in per_text_tag_analysis.values())
        for pattern in patterns
    }
    file_analysis = {
        FILENAME_KEY: file_path,
        PATTERNS_KEY: file_patterns_dict,
        PER_TEXT_TAG_KEY: per_text_tag_analysis
    }
    print(file_patterns_dict)
    return file_analysis


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
        common_string_ids = set(previous_file_data[PER_TEXT_TAG_KEY].keys()).intersection(
            set(current_file_data[PER_TEXT_TAG_KEY].keys())
        )
        for string_id in common_string_ids:
            previous_tag_patterns = previous_file_data[PER_TEXT_TAG_KEY][string_id]
            current_tag_patterns = current_file_data[PER_TEXT_TAG_KEY][string_id]
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
        print(Fore.YELLOW + "#" * 80)
        print(Fore.YELLOW + " " * 25 + "Mismatch in reports detected!")
        print(Fore.YELLOW + "#" * 80)
        print(Fore.BLUE + "#" * 10 + " Total missmatch: " + "#" * 10)
        for pattern in PATTERNS:
            prev_count = total_patterns_prev[pattern]
            curr_count = total_patterns_curr[pattern]
            change = total_patterns_change[pattern]
            if change == 0:
                continue

            print(
                Fore.BLUE + f"Pattern: '{pattern}', {abs(change)} {'more' if change > 0 else 'less'} than before. Before {prev_count} after {curr_count}")

        print(Fore.MAGENTA + "\t" + "#" * 10 + " Mismatched files: " + "#" * 10)
        for file, file_mismatches, text_tag_mismatches in mismatched_files:
            print(Fore.MAGENTA + f"\nFile: '{file}'")
            for pattern, counts in file_mismatches.items():
                prev_count, curr_count, change = counts
                print(
                    Fore.MAGENTA + f"\tPattern: '{pattern}', {abs(change)} {'more' if change > 0 else 'less'} than before. Before {prev_count} after {curr_count}")
            print(Fore.GREEN + "\t" + "#" * 10 + " Mismatched strings: " + "#" * 10)
            for string_id, tag_mismatches in text_tag_mismatches.items():
                print(Fore.GREEN + f"\tstring: '{string_id}'")
                for pattern, counts in tag_mismatches.items():
                    prev_count, curr_count, change = counts
                    print(
                        Fore.GREEN + f"\t\tPattern: '{pattern}', {abs(change)} {'more' if change > 0 else 'less'} than before. Before {prev_count} after {curr_count}")
    else:
        print(Fore.GREEN + "#" * 30)
        print(Fore.GREEN + "Versions match! Jolly good!")
        print(Fore.GREEN + "#" * 30)


def add_summary(current_analysis):
    file_analysis = current_analysis.pop(PER_FILE_KEY)

    current_analysis[SUMMARY_KEY] = {}
    for pattern in patterns:
        pattern_val = 0
        for file in file_analysis:
            pattern_val += file[PATTERNS_KEY][pattern]

        current_analysis[SUMMARY_KEY][pattern] = pattern_val

    print(f"Summary:")
    pp.pprint(current_analysis[SUMMARY_KEY])
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


def main():
    parser = argparse.ArgumentParser(description='Analyze and compare pattern occurrences in XML files.')
    parser.add_argument('--compare', metavar='FILE', type=str, help='a file path to a previous analysis for comparison')
    args = parser.parse_args()

    directory = './**/*.xml'
    xml_files = glob.glob(directory, recursive=True)

    print(f"Found {len(xml_files)} xml_files")

    current_analysis = {}
    current_analysis = add_meta_data(current_analysis)

    file_analysis = []
    current_analysis[PER_FILE_KEY] = file_analysis
    for file_path in xml_files:
        try:
            CURRENT_FILE_ISSUES.clear()
            file_analysis.append(analyze_patterns_in_file(file_path, patterns))
        except Exception as e:
            print(Fore.RED + f"Error processing {Fore.RED + file_path}: {e}")
            CURRENT_FILE_ISSUES.append(Fore.RED + f"Error: {e}" + Fore.RESET)
            failed_files[file_path] = list(CURRENT_FILE_ISSUES)

    if len(failed_files):
        print()
        print("#" * 80)
        print("\t\t\tFailed files:")
        for file in failed_files:
            print(f"\nFile: '{file}'")
            for issue in failed_files[file]:
                print("\t" + issue)

    current_analysis = add_summary(current_analysis)

    # Serialize the current analysis to a file
    serialize_analysis(current_analysis, build_file_name())

    if args.compare:
        print("\nComparing previous analysis to freshly-generated")
        previous_analysis = deserialize_analysis(args.compare)
        compare_analyses(previous_analysis, current_analysis, patterns)


if __name__ == "__main__":
    main()
