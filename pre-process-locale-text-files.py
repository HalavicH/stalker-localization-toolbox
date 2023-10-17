import glob
import codecs
import os
from lxml import etree
from colorama import Fore, init
import xmlschema

init(autoreset=True)  # Initialize colorama

# Define XML schema
schema_xml = """
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="string_table">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="string" maxOccurs="unbounded">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element name="text" type="xs:string" />
                        </xs:sequence>
                        <xs:attribute name="id" type="xs:string" use="required" />
                    </xs:complexType>
                </xs:element>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>
"""
schema = xmlschema.XMLSchema(schema_xml)


def process_includes(content, file_path):
    lines = content.splitlines()
    processed_lines = []
    base_dir = os.path.dirname(file_path)
    for line in lines:
        if line.strip().startswith('#include'):
            # Extract the included file path
            included_file_path = line.split('"')[1]
            included_file_path = os.path.join(base_dir, included_file_path)
            with codecs.open(included_file_path, 'r', encoding='windows-1251') as included_file:
                included_content = included_file.read()
                processed_lines.append(included_content)
        else:
            processed_lines.append(line)
    return '\n'.join(processed_lines)


def validate_xml(xml_string):
    try:
        # Replace -- with __ in comments
        xml_string = xml_string.replace('--', '__')
        xml_tree = etree.fromstring(xml_string)
        return xml_tree
    except etree.XMLSyntaxError as e:
        raise ValueError(f"XML Syntax Error: {e}")


def validate_schema(xml_tree):
    if not schema.is_valid(xml_tree):
        raise ValueError("Schema validation failed")


def check_and_add_header(xml_tree):
    if not xml_tree.docinfo.xml_version:
        print(Fore.YELLOW + "Warning: Missing XML header. Adding header.")
        return f'<?xml version="1.0" encoding="windows-1251"?>\n{etree.tostring(xml_tree, encoding="unicode")}'
    return etree.tostring(xml_tree, encoding='unicode')


def process_file(file_path):
    try:
        with codecs.open(file_path, 'r', encoding='windows-1251') as file:
            content = file.read()

        # Process #include statements
        content = process_includes(content, file_path)
        content = content.replace('<?xml version="1.0" encoding="windows-1251"?>', '').strip()
        content_utf8 = content.encode('utf-8').decode('utf-8')

        xml_tree = validate_xml(content_utf8)
        validate_schema(xml_tree)

        content_roundtrip = check_and_add_header(xml_tree)

        with codecs.open(file_path, 'w', encoding='windows-1251') as file:
            file.write(content_roundtrip)
        print(f'Processed {file_path}')

    except Exception as e:
        print(Fore.RED + f"Error processing {file_path}: {e}")


def main():
    directory = './**/*.xml'
    xml_files = glob.glob(directory, recursive=True)
    for file_path in xml_files:
        process_file(file_path)


if __name__ == "__main__":
    main()
