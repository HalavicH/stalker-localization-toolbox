import re
from lxml import etree


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
                    print(f"Misused '&'. Replacing & with &amp; at {line_number}:{column_number}")
                    corrected_line += '&amp;'
            else:
                corrected_line += line[column_number - 1]
            column_number += 1
        corrected_lines.append(corrected_line)
    corrected_xml_string = '\n'.join(corrected_lines)
    return corrected_xml_string


def check_and_correct_xml(xml_string):
    corrected_xml_string = escape_ampersands(xml_string)

    try:
        # Try parsing the corrected XML string
        etree.fromstring(corrected_xml_string)
        return corrected_xml_string
    except etree.XMLSyntaxError as e:
        # If there's still a syntax error, print the error and return the original string
        print(f"XML syntax error: {e}")
        return xml_string


# Example XML string
xml_string = """<root>
<child>Data & more data</child>
<child>10 &lt; 20 &amp; 30 &gt; 20</child>
</root>"""

# Check and correct the XML
corrected_xml_string = check_and_correct_xml(xml_string)

# Print the corrected XML
print(corrected_xml_string)
