import sys

import lxml.etree as etree
import textwrap
import re


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
    text = text.replace(r'\\n', '\n\\n')

    # Step 4: Wrap lines by word if longer than 85 char without inserting \n symbol
    lines = text.split('\n')
    wrapped_lines = []
    for line in lines:
        wrapped_line = textwrap.fill("\\n" + line, width=85, expand_tabs=False, replace_whitespace=False)
        for subline in wrapped_line.split("\n"):
            wrapped_lines.append(subline)

    # Step 3: Indent everything according to the position of the <text> tag
    indented_lines = [indent + line for line in wrapped_lines]

    return '\n' + '\n'.join(indented_lines)


def reformat_xml(xml_file):
    parser = etree.XMLParser(remove_blank_text=True)  # This will help preserve the indentations
    tree = etree.parse(xml_file, parser)
    root = tree.getroot()

    for string_elem in root:
        for text_elem in string_elem:
            text_elem.text = format_text(text_elem.text, ' ' * 12)  # Assuming indent of 12 spaces

    indent(root)
    # Write the reformatted XML to a new file
    tree.write(xml_file, encoding='windows-1251', xml_declaration=True, pretty_print=True)


# Call the function with your XML file
# reformat_xml(sys.argv[1])
reformat_xml('/Users/oleksandrkholiavko/IdeaProjects/stalker-gamma-0.9.1-ukr/gamedata/configs/text/eng/st_items_tools.xml')
