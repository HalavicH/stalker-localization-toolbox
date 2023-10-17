import glob
import codecs
from lxml import etree
import re
from colorama import Fore, init

encoding_string = '<?xml version="1.0" encoding="windows-1251"?>'

init(autoreset=True)


def format_xml(xml_string):
    # Replace -- with ** in comments before parsing, handle multiline comments with re.DOTALL
    xml_string = re.sub(r'<!--(.*?)-->', lambda x: '<!--' + x.group(1).replace('--', '**') + '-->', xml_string,
                        flags=re.DOTALL)

    if encoding_string in xml_string:
        xml_string.replace(encoding_string, '')
    else:
        print(Fore.YELLOW + f"File ... doesn't have encoding header in it")

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


def convert_encoding_roundtrip(file_path):
    # Read the file in Windows-1251 encoding
    with codecs.open(file_path, 'r', encoding='windows-1251') as file:
        content = file.read()

    formatted_text = format_xml(content.encode())
    # Write the roundtrip content back to the file
    with codecs.open(file_path, 'w', encoding='windows-1251') as file:
        file.write(formatted_text)


def main():
    # Define the directory to search (change this to your directory)
    directory = './**/*.xml'

    # Get the list of all XML files in the specified directory and subdirectories
    xml_files = glob.glob(directory, recursive=True)

    # Perform the encoding roundtrip for each XML file
    for file_path in xml_files:
        convert_encoding_roundtrip(file_path)
        print(f'Processed {file_path}')


if __name__ == "__main__":
    main()
