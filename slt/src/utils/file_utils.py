import codecs
import glob
import os

from src.config import PRIMARY_ENCODING
from src.log_config_loader import log


def find_xml_files(path):
    if os.path.isdir(path):
        glob_pattern = f'{path}/**/*.xml'
    else:
        glob_pattern = path

    xml_files = set(glob.glob(glob_pattern, recursive=True))
    if len(xml_files) == 0:
        raise ValueError(f"No XML file found under path: {path}")

    log.debug(f"Found following glob files: {xml_files}")
    log.info(f"Input files number: {len(xml_files)}")

    return xml_files


def read_xml(file_path, encoding=PRIMARY_ENCODING):
    with codecs.open(file_path, 'r', encoding=encoding) as file:
        return file.read()


def save_xml(file_path, xml_string, encoding=PRIMARY_ENCODING):
    if isinstance(xml_string, bytes):
        xml_string = xml_string.decode(encoding)

    with codecs.open(file_path, 'w', encoding=encoding) as file:
        return file.write(xml_string)
