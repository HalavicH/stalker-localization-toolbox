import re

def remove_xml_declaration(xml_string):
    # Regular expression pattern to match the XML declaration with any amount of whitespace
    pattern = re.compile(r'<\?xml\s+version\s*=\s*"1.0"\s+encoding\s*=\s*"windows-1251"\s*\?>', re.IGNORECASE)
    # Use re.sub to replace the matched text with an empty string
    xml_string_without_declaration = re.sub(pattern, '', xml_string)
    return xml_string_without_declaration

# Example XML string
xml_string = """
<?xml version="1.0"    encoding="windows-1251"   ?>
<root>
<child></child>
</root>"""

# Remove the XML declaration
xml_string_without_declaration = remove_xml_declaration(xml_string)

# Print the result
print(xml_string_without_declaration)
