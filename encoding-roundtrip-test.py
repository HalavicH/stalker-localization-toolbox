import glob
import codecs
import os
import sys

from lxml import etree
import re
from colorama import Fore, init

encoding_string = "<?xml version='1.0' encoding='WINDOWS-1251'?>"

init(autoreset=True)

CURRENT_FILE_ISSUES = []

def escape_ampersands(xml_string):
    lines = xml_string.split('\n')
    corrected_lines = []
    for line_number, line in enumerate(lines, start=1):
        corrected_line = ''
        column_number = 1
        while column_number <= len(line):
            if line[column_number - 1] == '&':
                # Check if it's part of a recognized character entity
                if re.match(r'&(amp|lt|gt|quot|apos|#x[0-9a-fA-F]+|#\d+);', line[column_number - 1:]):
                    # Skip past the character entity
                    entity_end = line[column_number - 1:].index(';') + column_number
                    corrected_line += line[column_number - 1:entity_end]
                    column_number = entity_end
                else:
                    message = Fore.YELLOW + f"Misused '&' at line:{line_number}, column:{column_number}. Replacing & with &amp;" + Fore.RESET
                    print(message)
                    CURRENT_FILE_ISSUES.append(message)
                    corrected_line += '&amp;'
            else:
                corrected_line += line[column_number - 1]
            column_number += 1
        corrected_lines.append(corrected_line)
    corrected_xml_string = '\n'.join(corrected_lines)
    return corrected_xml_string

def process_includes(content):
    lines = content.splitlines()
    processed_lines = []
    for line in lines:
        if line.strip().startswith('#include'):
            # Extract the included file path
            included_file_path = line.split('"')[1]
            included_file_path = os.path.join("./gamedata/configs", included_file_path.replace("\\", "/"))
            with codecs.open(included_file_path, 'r', encoding='windows-1251') as included_file:
                included_content = included_file.read()
                processed_lines.append(included_content)
            # os.rename(included_file_path, included_file_path + ".include")
        else:
            processed_lines.append(line)
    return '\n'.join(processed_lines)

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


def format_xml(xml_string):
    # Replace -- with ** in comments before parsing, handle multiline comments with re.DOTALL
    xml_string = re.sub(r'<!--(.*?)-->', lambda x: '<!--' + x.group(1).replace('-', '#') + '-->', xml_string,
                        flags=re.DOTALL)

    # Parse the XML string
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(xml_string, parser)

    # Function to add indentation and a blank line before comments
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

    indent(root)

    # Convert the XML tree to a string
    formatted_xml = etree.tostring(root, encoding='unicode')

    # Add a blank line before comments
    formatted_xml = re.sub(r'(\s)<!--', r'\1\n<!--', formatted_xml)

    return formatted_xml


def process_file(file_path):
    # Read the file in Windows-1251 encoding
    with codecs.open(file_path, 'r', encoding='windows-1251') as file:
        content = file.read()

    # copy file content from includes
    content = process_includes(content)

    # Replace '&' with &amp;
    content = escape_ampersands(content)

    # remove encoding
    content_no_declaration = remove_xml_declaration(content, file_path)

    # Format text
    formatted_text = format_xml(content_no_declaration)

    # Append encoding
    formatted_text = encoding_string + "\n" + formatted_text

    if content != formatted_text:
        print("Modified")

    # Write the roundtrip content back to the file
    with open(file_path, 'wb', ) as file:
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
