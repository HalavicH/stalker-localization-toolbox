import codecs
import os
import re

from lxml import etree
from lxml.etree import _Element

from sltools.config import PRIMARY_ENCODING
from sltools.log_config_loader import log
from sltools.utils.colorize import cf_yellow, cf_red
from sltools.utils.error_utils import log_and_save_error

declaration_str = "<?xml version='1.0' encoding='WINDOWS-1251'?>"


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
    return xml_string_without_declaration, is_valid_doc_info(doc_info, file_path, log_and_save_err)


def parse_doc_info(xml_string: str):
    parser = etree.XMLParser(recover=True)
    tree: _Element = etree.fromstring(xml_string.encode(PRIMARY_ENCODING), parser=parser)
    return tree.getroottree().docinfo


def is_valid_doc_info(doc_info, file_path=None, log_and_save_err=None):
    version = doc_info.xml_version
    encoding_lower = doc_info.encoding.lower()
    if version != '1.0' or encoding_lower != PRIMARY_ENCODING:
        message = cf_yellow(f"Warning: File {file_path} has invalid header in it")
        if log_and_save_err:
            log_and_save_error(file_path, message, level='warning')
        else:
            version_message = f"Expected version='1.0' got '{cf_red(version)}'" if version != '1.0' else ""
            encoding_message = f"Expected encoding='{PRIMARY_ENCODING}' got '{cf_red(encoding_lower)}'" if encoding_lower != PRIMARY_ENCODING else ""
            raise ValueError(f"Wrong XML declaration. {version_message}{encoding_message}")
        return False

    return True


def parse_xml_root(xml_string):
    if isinstance(xml_string, str):
        log.debug(f"Provided plain string. Encoding to {PRIMARY_ENCODING}")
        xml_string = xml_string.encode(PRIMARY_ENCODING)

    parser = etree.XMLParser(remove_blank_text=True)
    return etree.fromstring(xml_string, parser)


def is_include_present(xml_string):
    pattern = re.compile(r'#include "(.*?\.xml)"')
    matches = pattern.findall(xml_string)
    return len(matches) != 0


def resolve_xml_includes(xml_string):
    trailing = "\n" if xml_string[-1] == "\n" else ""
    lines = xml_string.splitlines()
    processed_lines = []
    for line in lines:
        if line.strip().startswith('#include'):
            # Extract the included file path
            included_file_path = line.split('"')[1]
            included_file_path = os.path.join("../../gamedata/configs", included_file_path.replace("\\", "/"))
            with codecs.open(included_file_path, 'r', encoding=PRIMARY_ENCODING) as included_file:
                included_content = included_file.read()
                processed_lines.append(included_content)
            # os.rename(included_file_path, included_file_path + ".include")
        else:
            processed_lines.append(line)
    return '\n'.join(processed_lines) + trailing


# Error formatters
def analyze_xml_parser_error(error, file=None, string=None):
    hyphen_within_comment = "Double hyphen within comment"
    err_str = str(error)
    if hyphen_within_comment in err_str:
        return True, "XML file has '--' witin comment. First occurrence at: " + err_str.replace(hyphen_within_comment,
                                                                                                "")
    elif "Document is empty" in err_str:
        return True, "XML file is empty which is not allowed"
    else:
        return True, f"Can't parse root tag. Error {error}"


# Formatting utils
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


def add_blank_line_before_comments(formatted_xml):
    lines = formatted_xml.split('\n')
    output_lines = []
    in_comment_block = False
    for line in lines:
        if line.strip().startswith('<!--'):
            if not in_comment_block:
                output_lines.append('')  # Add a blank line before a new comment block
                in_comment_block = True
        else:
            in_comment_block = False
        output_lines.append(line)
    return '\n'.join(output_lines)


class XmlFileProcessingError(Exception):
    pass


def format_xml_string(xml_string, file_path="Not provided"):
    # Parse the XML string
    root = None
    try:
        root = parse_xml_root(xml_string)
    except Exception as e:
        _, msg = analyze_xml_parser_error(e)
        log_and_save_error(file_path, msg)
        raise XmlFileProcessingError(file_path + "|" + msg)

    # Function to add indentation and a blank line before comments
    indent(root)

    # Convert the XML tree to a string
    # formatted_xml_bytes: bytes = etree.tostring(root, encoding=windows_1251)
    formatted_xml_string = to_utf_string_with_proper_declaration(root)

    # Add a blank line before comments
    updated_xml_str = add_blank_line_before_comments(formatted_xml_string)

    return updated_xml_str.strip() + "\n"


def to_utf_string_with_proper_declaration(root):
    return (etree.tostring(root, xml_declaration=True, encoding='utf-8')
            .decode('utf-8')).replace("<?xml version='1.0' encoding='utf-8'?>", declaration_str)


# Text utils
def extract_text_from_xml(xml_string):
    root = parse_xml_root(xml_string)
    texts = [elem.text for elem in root.xpath('//text') if elem.text and elem.text.strip()]
    return '.\n'.join(texts)


#############
# Fix utils #
#############
def fix_illegal_comments(xml_string):
    def replace_dashes(match):
        comment_content = match.group(1)
        # Replace sequences of '-' (more than one) with equivalent number of '#'
        return re.sub(r'-{2,}', lambda x: '=' * len(x.group()), comment_content)

    return re.sub(r'<!--(.*?)-->', lambda x: '<!--' + replace_dashes(x) + '-->', xml_string, flags=re.DOTALL)


def fix_xml_declaration(xml_string, file_path):
    no_decl, is_valid_decl = remove_xml_declaration(xml_string, file_path)

    if not is_valid_decl:
        msg = "The XML declaration is incorrect. Fixing..."
        log.info(msg)

    return declaration_str + no_decl


def fix_ampersand_misuse(xml_string):
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
                    message = cf_yellow(
                        f"Misused '&' at line:{line_number}, column:{column_number}. Replacing & with &amp;")
                    log.info(message)
                    corrected_line += '&amp;'
            else:
                corrected_line += line[column_number - 1]
            column_number += 1
        corrected_lines.append(corrected_line)
    corrected_xml_string = '\n'.join(corrected_lines)
    return corrected_xml_string


def fix_possible_errors(xml_string, file_path):
    # String manipulation
    log.debug("Try to detect and fix comments")
    fixed_comments = fix_illegal_comments(xml_string)
    log.debug("Try to detect and fix ampersand issues")
    fixed_ampersand = fix_ampersand_misuse(fixed_comments)
    log.debug("Try to detect and resolve includes")
    resolved_includes = resolve_xml_includes(fixed_ampersand)

    # XML DOM parser manipulation
    log.debug("Try to detect and fix XML declaration")
    fixed_declaration = fix_xml_declaration(resolved_includes, file_path)
    log.debug("Done with fixing")
    return fixed_declaration
