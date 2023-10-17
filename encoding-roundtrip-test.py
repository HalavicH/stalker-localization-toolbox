import glob
import codecs
from lxml import etree
import re
from colorama import Fore, init

encoding_string = '<?xml version="1.0" encoding="windows-1251"?>'

init(autoreset=True)


def remove_xml_declaration(xml_string):
    # Regular expression pattern to match the XML declaration with any amount of whitespace
    pattern = re.compile(r'<\?xml.*?\?>', re.IGNORECASE)
    # Use re.sub to replace the matched text with an empty string
    string_was_here = 'xml_encoding_string_was_here'
    xml_string_without_declaration = re.sub(pattern, string_was_here, xml_string)

    if string_was_here in xml_string_without_declaration:
        xml_string_without_declaration = xml_string_without_declaration.replace(string_was_here, '')
    else:
        print(Fore.YELLOW + f"File ... doesn't have encoding header in it")

    return xml_string_without_declaration


def format_xml(xml_string):
    # Replace -- with ** in comments before parsing, handle multiline comments with re.DOTALL
    xml_string = re.sub(r'<!--(.*?)-->', lambda x: '<!--' + x.group(1).replace('--', '**') + '-->', xml_string,
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


def convert_encoding_roundtrip(file_path):
    # Read the file in Windows-1251 encoding
    with codecs.open(file_path, 'r', encoding='windows-1251') as file:
        content = file.read()

    # remove encoding
    content_no_declaration = remove_xml_declaration(content)

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
    # Define the directory to search (change this to your directory)
    directory = './**/*.xml'

    # Get the list of all XML files in the specified directory and subdirectories
    xml_files = glob.glob(directory, recursive=True)

    # Perform the encoding roundtrip for each XML file
    for file_path in xml_files:
        print(f'Processing {file_path}')
        convert_encoding_roundtrip(file_path)


if __name__ == "__main__":
    main()
