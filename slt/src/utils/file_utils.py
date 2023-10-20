import glob
import os

from src.log_config_loader import get_main_logger

log = get_main_logger()


def find_xml_files(path):
    if os.path.isdir(path):
        glob_pattern = f'{path}/**/*.xml'
    else:
        glob_pattern = path

    xml_files = set(glob.glob(glob_pattern, recursive=True))
    log.debug(f"Found following glob files: {xml_files}")
    log.info(f"Input files number: {len(xml_files)}")

    return xml_files
