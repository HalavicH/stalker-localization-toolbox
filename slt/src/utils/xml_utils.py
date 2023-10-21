import codecs
import os
import re

from lxml import etree
from lxml.etree import _Element

from src.command_names import windows_1251
from src.utils.colorize import cf_yellow, cf_green, cf_red
from src.utils.error_utils import log_and_save_error


def read_xml(file_path, encoding='windows-1251'):
    with codecs.open(file_path, 'r', encoding=encoding) as file:
        return file.read()


def remove_xml_declaration(xml_string, file_path, log_and_save_err=True):
    doc_info = parse_doc_info(xml_string)

    # Regular expression pattern to match the XML declaration with any amount of whitespace
    pattern = re.compile(r'<\?xml.*?\?>', re.IGNORECASE)
    # Use re.sub to replace the matched text with an empty string
    string_was_here = 'xml_encoding_string_was_here'
    xml_string_without_declaration = re.sub(pattern, string_was_here, xml_string)

    if string_was_here not in xml_string_without_declaration:
        message = cf_yellow(f"Warning: File {file_path} doesn't have encoding header in it")
        if log_and_save_err:
            log_and_save_error(file_path, message, level='warning')
        return xml_string_without_declaration, False

    xml_string_without_declaration = xml_string_without_declaration.replace(string_was_here, '')
    version = doc_info.xml_version
    encoding_lower = doc_info.encoding.lower()
    if version != '1.0' or encoding_lower != windows_1251:
        message = cf_yellow(f"Warning: File {file_path} has invalid header in it")
        if log_and_save_err:
            log_and_save_error(file_path, message, level='warning')
        else:
            version_message = f"Expected version='1.0' got '{cf_red(version)}'" if version != '1.0' else ""
            encoding_message = f"Expected encoding='{windows_1251}' got '{cf_red(encoding_lower)}'" if encoding_lower != windows_1251 else ""
            raise ValueError(f"Wrong XML declaration. {(version_message)}{encoding_message}")
        return xml_string_without_declaration, False

    return xml_string_without_declaration, True


def parse_doc_info(xml_string: str):
    parser = etree.XMLParser(recover=True)
    tree: _Element = etree.fromstring(xml_string.encode(windows_1251), parser=parser)
    return tree.getroottree().docinfo


def check_doc_info(doc_info):
    if doc_info.xml_version != '1.0' or doc_info.encoding.lower() != windows_1251:
        pass


def parse_xml_root(xml_string):
    parser = etree.XMLParser(remove_blank_text=True)
    return etree.fromstring(xml_string, parser)


def fix_broken_comments(xml_string):
    return re.sub(r'<!--(.*?)-->',
                  lambda x: '<!--' + x.group(1).replace('--', '**') + '-->', xml_string,
                  flags=re.DOTALL)


def is_include_present(xml_string):
    pattern = re.compile(r'#include "(.*?\.xml)"')
    matches = pattern.findall(xml_string)
    return len(matches) != 0


def resolve_xml_includes(xml_string):
    lines = xml_string.splitlines()
    processed_lines = []
    for line in lines:
        if line.strip().startswith('#include'):
            # Extract the included file path
            included_file_path = line.split('"')[1]
            included_file_path = os.path.join("../../gamedata/configs", included_file_path.replace("\\", "/"))
            with codecs.open(included_file_path, 'r', encoding='windows-1251') as included_file:
                included_content = included_file.read()
                processed_lines.append(included_content)
            # os.rename(included_file_path, included_file_path + ".include")
        else:
            processed_lines.append(line)
    return '\n'.join(processed_lines)


# Error formatters
def analyze_xml_parser_error(error, file=None, string=None):
    hyphen_within_comment = "Double hyphen within comment"
    err_str = str(error)
    if hyphen_within_comment in err_str:
        return True, "XML file has '--' witin comment. First occurrence at: " + err_str.replace(hyphen_within_comment, "")
    elif "Document is empty" in err_str:
        return True, "XML file is empty which is not allowed"
    else:
        return True, f"Can't parse root tag. Error {error}"

