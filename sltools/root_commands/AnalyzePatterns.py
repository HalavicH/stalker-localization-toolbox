import json
import subprocess
import time
from datetime import datetime

from langdetect import LangDetectException
from rich import get_console, pretty

from sltools.baseline.command_baseline import AbstractCommand
from sltools.log_config_loader import log
from sltools.old.commands.format_xml import error_str, format_xml_text_entries, to_yes_no
from sltools.old.commands.utils.common import get_xml_files_and_log
from sltools.old.config import UNKNOWN_LANG, TOO_LITTLE_DATA, min_recognizable_text_length
from sltools.utils.colorize import cf_green, cf_red, cf_yellow, cf_cyan, rich_guard, cf_blue, cf_magenta
from sltools.utils.error_utils import log_and_save_error, interpret_error
from sltools.utils.file_utils import read_xml, save_xml
from sltools.utils.lang_utils import trn
from sltools.utils.misc import create_table, exception_originates_from, detect_language
from sltools.utils.plain_text_utils import tabwidth, format_text_entry, purify_text, analyze_patterns_in_text, check_placeholders
from sltools.utils.xml_utils import fix_possible_errors, format_xml_string, parse_xml_root, indent, to_utf_string_with_proper_declaration, \
    add_blank_line_before_comments, extract_text_from_xml

# JUNK
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
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                                         text=True).strip().replace('/', '-').replace(' ', '_')
        commit_name = subprocess.check_output(['git', 'log', '-1', '--pretty=format:%s'],
                                              text=True).strip().replace(' ', '_').replace('/', '-').replace(':', '-')
        commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], text=True).strip()
        file_name = 'pattern-analysis_br-%s_cmd-%s_hash-%s_time-%d.txt' % (branch, commit_name, commit_hash, timestamp)
    except subprocess.CalledProcessError:
        file_name = 'pattern-analysis_%d.txt' % timestamp
    return file_name


def aggregate_data(detailed_analysis):
    sum_pattens = {}
    sum_errors = {}
    for name, string_report in detailed_analysis.items():
        for pattern_type, patterns_stats in string_report[PATTERNS_KEY].items():
            sum_pattens[pattern_type] = sum_pattens.get(pattern_type) or {}
            for pattern, cnt in patterns_stats.items():
                if sum_pattens[pattern_type].get(pattern) is not None:
                    sum_pattens[pattern_type][pattern] += cnt
                else:
                    sum_pattens[pattern_type][pattern] = cnt

        string_errors = string_report[PATTERN_ERRORS_KEY]
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
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                                         text=True).strip().replace('/', '-').replace(' ', '_')
        commit_name = subprocess.check_output(['git', 'log', '-1', '--pretty=format:%s'],
                                              text=True).strip().replace(' ', '_').replace('/', '-')
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
        log.always(trn("Missing files in current analysis: %s") % ', '.join(missing_files))
    if extra_files:
        log.always(trn("Extra files in current analysis: %s") % ', '.join(extra_files))

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
        log.always(cf_yellow(trn("###### Mismatch in reports detected! ######")))
        log.always(cf_yellow("#" * 80))
        log.always(cf_blue("#" * 10 + trn(" Total missmatch: ") + "#" * 10))
        for pattern in PATTERNS:
            prev_count = total_patterns_prev[pattern]
            curr_count = total_patterns_curr[pattern]
            change = total_patterns_change[pattern]
            if change != 0:
                log.always(cf_blue(
                    trn("Pattern: '%s', %d %s than before. Before %d after %d") % (pattern, abs(change), get_action(change), prev_count, curr_count)))

        log.always(cf_magenta("\t" + "#" * 10 + trn(" Mismatched files: ") + "#" * 10))
        for file, file_mismatches, text_tag_mismatches in mismatched_files:
            log.always(cf_magenta(trn("File: '%s'") % file))
            for pattern, counts in file_mismatches.items():
                prev_count, curr_count, change = counts
                log.always(cf_magenta(
                    trn("Pattern: '%s', %d %s than before. Before %d after %d") % (pattern, abs(change), get_action(change), prev_count, curr_count)))

            log.always(cf_magenta("\t" + "#" * 10 + trn(" Mismatched strings: ") + "#" * 10))
            for string_id, tag_mismatches in text_tag_mismatches.items():
                log.always("\t" + trn("String: '%s'") % string_id)
                for pattern, counts in tag_mismatches.items():
                    prev_count, curr_count, change = counts
                    log.always(cf_green(
                        trn("Pattern: '%s', %d %s than before. Before %d after %d") % (pattern, abs(change), get_action(change), prev_count, curr_count)))
    else:
        log.always(cf_green("#" * 30))
        log.always(cf_green(trn("Versions match! Jolly good!")))
        log.always(cf_green("#" * 30))


def get_action(change):
    return trn('more') if change > 0 else trn('less')


class AnalyzePatterns(AbstractCommand):
    # Metadata
    ##########
    def get_name(self) -> str:
        return "analyze-patterns"

    def get_aliases(self) -> list:
        return ['ap']

    def _get_help(self) -> str:
        return trn('Analyze patterns in a file or directory')

    def _setup_parser_args(self, parser):
        parser.add_argument('paths', nargs='*', help=trn('Paths to files or directories'))
        parser.add_argument('--save', action='store_true', default=False,
                            help=trn('Save detailed report as JSON file (for future comparison)'))

    # Execution
    ###########
    def _process_file(self, file_path, per_file_results: dict, args):
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
                string_analysis[PATTERN_ERRORS_KEY] = check_placeholders(text_content, xml_string)
                per_string_analysis[string_id] = string_analysis

        file_patterns_summary, file_patterns_errors = aggregate_data(per_string_analysis)

        per_file_results[file_path] = {
            FILENAME_KEY: file_path,
            PATTERNS_KEY: file_patterns_summary,
            PATTERN_ERRORS_KEY: file_patterns_errors,
            PER_STRING_KEY: per_string_analysis
        }

    def execute(self, args) -> dict:
        files = get_xml_files_and_log(args.paths, trn("Analyzing patterns usage and errors"))

        results = {}
        results = add_meta_data(results)
        per_file_results = {}
        results[PER_FILE_KEY] = per_file_results

        self.process_files_with_progressbar(args, files, per_file_results, True)

        results = add_summary(results)

        log.info(trn("Total processed files: %s") % len(files))

        if args.save:
            filename = build_file_name()
            log.always(trn("Saving the report at [cyan]%s[/cyan]") % rich_guard(filename))
            serialize_analysis(results, filename)

        return results

    # Displaying
    ############
    def display_result(self, result: dict):
        log.always(trn("Displaying report"))
        log.always(trn("Summary:"))

        patterns_report = result[SUMMARY_KEY][PATTERNS_KEY]
        errors = result[SUMMARY_KEY][PATTERN_ERRORS_KEY]
        log.always(trn("Patterns:"))
        for pattern_type, patterns in patterns_report.items():
            log.always(trn("\t%s:") % cf_yellow(pattern_type))
            for pattern, cnt in patterns.items():
                log.always(trn("\t\t%s: %s") % (cf_green(pattern), cf_cyan(cnt)))

        if len(errors) == 0:
            log.always(cf_green(trn("No pattern syntax errors detected")))
            return

        log.always(cf_red("#" * 80))
        log.always(cf_red(trn("Errors:")))
        log.always(cf_red("#" * 80))
        for filename, file_report in errors.items():
            log.always(trn("[cyan]In file:[/cyan] %s:") % cf_yellow(filename))

            for string, string_report in file_report.items():
                log.always(trn("[cyan]In string with id:[/cyan] '%s'") % cf_green(string))

                for error in string_report:
                    row = error['position']['row']
                    col = error['position']['column']
                    cause = error['type']
                    snippet_lines = error['snippet'].split("\n")

                    log.always(cf_red(trn("Error: %s")) % cause + trn(". Row: %s, column %s") % (row, col))
                    for line in snippet_lines:
                        log.always(trn("[grey53]%s") % line)
                    log.always("")

        log.always(trn("Meta-data:"))
        pretty.pprint(result[META_DATA_KEY])
