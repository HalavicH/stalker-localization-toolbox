import glob
import json
import argparse
import subprocess
import time

SUMMARY_KEY = "summary"
PER_FILE_KEY = "per_file"

FILENAME_KEY = "file_name"
PATTERNS_KEY = "patterns"

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


def analyze_patterns_in_file(file_path, patterns):
    print("Analyzing file: " + file_path)

    with open(file_path, 'r', encoding='windows-1251', errors='ignore') as file:
        text = file.read()
    patterns_dict = {
        FILENAME_KEY: file_path,
        PATTERNS_KEY: {pattern: text.count(pattern) for pattern in patterns}
    }
    print(patterns_dict[PATTERNS_KEY])
    return patterns_dict


def compare_analyses(previous_analysis, current_analysis, patterns):
    mismatched_files = []
    for current, previous in zip(current_analysis[PER_FILE_KEY], previous_analysis[PER_FILE_KEY]):
        mismatched_patterns = []
        for pattern in patterns:
            previous_count = previous[PATTERNS_KEY].get(pattern, 0)
            current_count = current[PATTERNS_KEY].get(pattern, 0)
            if previous_count != current_count:
                difference = current_count - previous_count
                change = f"{abs(difference)} more" if difference > 0 else f"{abs(difference)} less"
                mismatched_patterns.append((pattern, change))
        if mismatched_patterns:
            mismatched_files.append((current[FILENAME_KEY], mismatched_patterns))

    if mismatched_files:
        print("#" * 80)
        print("\t\tMismatched files:")
        for file, mismatches in mismatched_files:
            print(f"\nFile: '{file}'")
            for pattern, change in mismatches:
                print(f"\tPattern: '{pattern}', {change} than before")
    else:
        print("#" * 30)
        print("Versions match! Jolly good!")
        print("#" * 30)


def add_summary(file_analysis):
    results = {
        SUMMARY_KEY: {},
        PER_FILE_KEY: None
    }
    for pattern in patterns:
        pattern_val = 0
        for file in file_analysis:
            pattern_val += file[PATTERNS_KEY][pattern]

        results[SUMMARY_KEY][pattern] = pattern_val

    results[PER_FILE_KEY] = file_analysis
    print(f"Summary: {results[SUMMARY_KEY]}")

    return results


def main():
    parser = argparse.ArgumentParser(description='Analyze and compare pattern occurrences in XML files.')
    parser.add_argument('--compare', metavar='FILE', type=str, help='a file path to a previous analysis for comparison')
    args = parser.parse_args()

    directory = './**/*.xml'
    xml_files = glob.glob(directory, recursive=True)

    print(f"Found {len(xml_files)} xml_files")
    file_analysis = [analyze_patterns_in_file(file_path, patterns) for file_path in xml_files]

    current_analysis = add_summary(file_analysis)

    # Serialize the current analysis to a file
    timestamp = int(time.time())
    serialize_analysis(current_analysis, build_file_name())

    if args.compare:
        print("\nComparing previous analysis to freshly-generated")
        previous_analysis = deserialize_analysis(args.compare)
        compare_analyses(previous_analysis, current_analysis, patterns)


if __name__ == "__main__":
    main()
