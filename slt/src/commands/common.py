# Given the common patterns observed, let's extract some helper functions:
from rich.progress import Progress

from src.log_config_loader import log
from src.utils.colorize import cf_green
from src.utils.file_utils import find_xml_files
from src.utils.misc import get_term_width


# 1. Get the list of XML files and log the number of files
def get_xml_files_and_log(path, action_msg):
    files = find_xml_files(path)
    log.always(f"{action_msg} {cf_green(len(files))} files")
    return files


# 2. Determine the maximum file width for display based on terminal width
def get_max_file_width_for_display():
    term_width = get_term_width()
    return term_width - 80 if term_width > 130 else term_width - 60


# 3. Process each file with progress indication
def process_files_with_progress(files, process_func, results):
    max_file_width = get_max_file_width_for_display()
    with Progress() as progress:
        task = progress.add_task("", total=len(files))
        for i, file_path in enumerate(files):
            formatted_file = format_filename_for_display(file_path, max_file_width)
            progress_description = f"Processing file [green]#{i:03}[/] with name [green]{formatted_file}[/]"
            progress.update(task, completed=i, description=progress_description)
            log.debug(f"Processing file #{i} name: {file_path}")
            process_func(file_path, results)


def format_filename_for_display(file, max_file_width):
    if len(file) > max_file_width:
        return "..." + file[-(max_file_width - 5):]
    else:
        return file.ljust(max_file_width)
