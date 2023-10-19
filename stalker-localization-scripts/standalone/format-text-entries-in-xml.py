import codecs
import glob
import re
import sys

import colorama
import lxml.etree as etree
import textwrap

from colorama import Fore

colorama.init(autoreset=True)

CURRENT_FILE_ISSUES = []

encoding_string = "<?xml version='1.0' encoding='WINDOWS-1251'?>"

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


def remove_xml_declaration(xml_string, file_path):
    # Regular expression pattern to match the XML declaration with any amount of whitespace
    pattern = re.compile(r'<\?xml.*?\?>', re.IGNORECASE)
    # Use re.sub to replace the matched text with an empty string
    string_was_here = 'xml_encoding_string_was_here'
    xml_string_without_declaration = re.sub(pattern, string_was_here, xml_string)

    if string_was_here in xml_string_without_declaration:
        xml_string_without_declaration = xml_string_without_declaration.replace(string_was_here, '')
    else:
        reset = Fore.YELLOW + f"Warning: File {file_path} doesn't have encoding header in it" + Fore.RESET
        print(reset)
        CURRENT_FILE_ISSUES.append(reset)

    return xml_string_without_declaration

def process_file(xml_file):
    with codecs.open(xml_file, 'r', encoding='windows-1251') as file:
        content = file.read()

    content = remove_xml_declaration(content, xml_file)

    parser = etree.XMLParser(remove_blank_text=True)  # This will help preserve the indentations
    root = etree.fromstring(content, parser)

    for string_elem in root:
        for text_elem in string_elem:
            text_elem.text = format_text(text_elem.text, ' ' * 12)  # Assuming indent of 12 spaces

    indent(root)

    # Convert the XML tree to a string
    formatted_xml = etree.tostring(root, encoding='unicode')

    # Add a blank line before comments
    formatted_xml = re.sub(r'(\s)<!--', r'\1\n<!--', formatted_xml)

    # Append encoding
    formatted_text = encoding_string + "\n" + formatted_xml

    # Write the reformatted XML to a new file
    # Write the roundtrip content back to the file
    with open(xml_file, 'wb', ) as file:
        file.write(formatted_text.encode('windows-1251'))


def main():
    if len(sys.argv) == 2:
        print("Singlefile mode")
        process_file(sys.argv[1])
        return

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
