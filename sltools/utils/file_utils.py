import codecs
import glob
import os

from sltools.old.config import PRIMARY_ENCODING
from sltools.log_config_loader import log
from sltools.utils.lang_utils import trn


def find_xml_files(path):
    if os.path.isdir(path):
        glob_pattern = '%s/**/*.xml' % path
    else:
        glob_pattern = path

    xml_files = set(glob.glob(glob_pattern, recursive=True))
    if len(xml_files) == 0:
        raise ValueError(trn("No XML file found under path: '%s'.\nPlease provide path which contains xml files") % path)

    log.debug(trn("Found following glob files: %s") % xml_files)
    log.info(trn("Input files number: %s") % len(xml_files))

    return xml_files


def read_xml(file_path, encoding=PRIMARY_ENCODING):
    with codecs.open(file_path, 'r', encoding=encoding) as file:
        return file.read()


def save_xml(file_path, xml_string, encoding=PRIMARY_ENCODING):
    if isinstance(xml_string, bytes):
        xml_string = xml_string.decode(encoding)

    with codecs.open(file_path, 'w', encoding=encoding) as file:
        return file.write(xml_string)
