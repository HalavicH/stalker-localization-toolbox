import glob

import colorama
import lxml.etree as etree
import textwrap

from colorama import Fore

colorama.init(autoreset=True)

CURRENT_FILE_ISSUES = []

def indent(elem, level=0):
    i = "\n" + level * "    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def format_text(text, indent):
    # Step 1: Collapse the text into one line
    text = ' '.join(text.split())

    # Step 2: Place line breaks before \n
    text = text.replace('\\n', '\n\\n')

    # Step 4: Wrap lines by word if longer than 85 char without inserting \n symbol
    lines = text.split('\n')
    wrapped_lines = []
    for line in lines:
        wrapped_line = textwrap.fill(line, width=85, expand_tabs=False, replace_whitespace=False)
        for subline in wrapped_line.split("\n"):
            wrapped_lines.append(subline)

    # Step 3: Indent everything according to the position of the <text> tag
    indented_lines = [indent + line for line in wrapped_lines]

    # Remove 2 characters so '\n' is not at the same level as other text
    for i in range(0, len(indented_lines)):
        if "\\n" in indented_lines[i]:
            indented_lines[i] = indented_lines[i][2:]

    return '\n' + '\n'.join(indented_lines) + '\n' + (" " * 8)


def process_file(xml_file):
    parser = etree.XMLParser(remove_blank_text=True)  # This will help preserve the indentations
    tree = etree.parse(xml_file, parser)
    root = tree.getroot()

    for string_elem in root:
        for text_elem in string_elem:
            text_elem.text = format_text(text_elem.text, ' ' * 12)  # Assuming indent of 12 spaces

    indent(root)

    # Write the reformatted XML to a new file
    tree.write(xml_file, encoding='windows-1251', xml_declaration=True, pretty_print=True)


def main():
    # Define the directory to search (change this to your directory)
    directory = './**/*.xml'

    failed_files = {}
    # Get the list of all XML files in the specified directory and subdirectories
    xml_files = glob.glob(directory, recursive=True)

    # Perform the encoding roundtrip for each XML file
    for file_path in xml_files:
        try:
            print(f'Processing {file_path}')
            CURRENT_FILE_ISSUES.clear()
            process_file(file_path)
        except Exception as e:
            print(Fore.RED + f"Error processing {Fore.RED + file_path}: {e}")
            CURRENT_FILE_ISSUES.append(Fore.RED + f"Error: {e}" + Fore.RESET)
            failed_files[file_path] = list(CURRENT_FILE_ISSUES)

    print()
    print("#" * 80)
    print("\t\t\tFailed files:")
    for file in failed_files:
        print(f"\nFile: '{file}'")
        for issue in failed_files[file]:
            print("\t" + issue)

if __name__ == "__main__":
    main()
