import glob
import time


def count_patterns_in_text(text, patterns):
    counts = {pattern: text.count(pattern) for pattern in patterns}
    return counts


def analyze_patterns_in_file(file_path, patterns):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        text = file.read()
    return count_patterns_in_text(text, patterns)


def main():
    # Define the directory to search (change this to your directory)
    directory = './**/*.xml'

    # Define the patterns to look for
    patterns = ['\\n', '%s']

    # Initialize a dictionary to hold total counts
    total_counts = {pattern: 0 for pattern in patterns}

    # Get the list of all XML files in the specified directory and subdirectories
    xml_files = glob.glob(directory, recursive=True)

    # Initialize a list to hold the result strings
    result_strings = []

    # Analyze each XML file
    for file_path in xml_files:
        print(f'Analyzing {file_path}')
        counts = analyze_patterns_in_file(file_path, patterns)
        result_string = f'{file_path}:\n' + '\n'.join([f'{pattern}: {count}' for pattern, count in counts.items()])
        print(result_string)
        result_strings.append(result_string)

        # Update total counts
        for pattern, count in counts.items():
            total_counts[pattern] += count

    # Print and save the total counts
    total_result_string = 'Total:\n' + '\n'.join([f'{pattern}: {count}' for pattern, count in total_counts.items()])
    print(total_result_string)
    result_strings.append(total_result_string)

    # Get the current timestamp
    timestamp = int(time.time())

    # Write the results to a file
    with open(f'pattern-analysis-{timestamp}.txt', 'w') as file:
        file.write('\n\n'.join(result_strings))


if __name__ == "__main__":
    main()
