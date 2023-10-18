import glob
import os


def get_list_of_files(file_or_dirpath):
    if os.path.isdir(file_or_dirpath):
        xml_files = glob.glob(f'{file_or_dirpath}/**/**/*.xml', recursive=True)
    else:
        xml_files = [file_or_dirpath]
