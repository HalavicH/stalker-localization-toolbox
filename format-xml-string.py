from lxml import etree
import re

def format_xml(xml_string):
    # Replace -- with ** in comments before parsing, handle multiline comments with re.DOTALL
    xml_string = re.sub(r'<!--(.*?)-->', lambda x: '<!--' + x.group(1).replace('--', '**') + '-->', xml_string, flags=re.DOTALL)

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

# Example XML string
xml_string = """
<string_table>
	<string id="st_ignite_fire">
	<text>Розпалити ($$ACTION_USE$$)</text>
</string>
<string id="st_ignite_wait"> <!-- My comment in very uncomfortable place ------------ -->

<text>
Треба трохи почекати, перш ніж розпалювати знову</text>

</string>
<string id="st_ignite_far">
<text>Або поряд немає багаття, або Ви стоїте занадто далеко</text>
</string>
<string id="st_extinguish_fire">
<text>Загасити ($$ACTION_USE$$)</text>
</string>
<string id="actor_inventory_box_use">
<text>Відкрити ($$ACTION_USE$$)</text>
</string>
</string_table>
"""

# Get the formatted XML
formatted_xml = format_xml(xml_string)

# Print the formatted XML
print(formatted_xml)
