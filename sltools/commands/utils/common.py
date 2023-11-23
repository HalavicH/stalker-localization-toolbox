from rich import get_console
from rich.progress import Progress

from sltools.log_config_loader import log
from sltools.utils.colorize import cf_green
from sltools.utils.file_utils import find_xml_files
from sltools.utils.git_utils import is_allowed_to_continue
from sltools.utils.misc import get_term_width
from sltools.utils.lang_utils import _tr  # Ensure this import is included for _tr function


# 1. Get the list of XML files and log the number of files
def get_xml_files_and_log(paths, action_msg):
    all_files = []
    for path in paths:
        all_files.extend(find_xml_files(path))
    log.always(_tr("%s %s files") % (action_msg, cf_green(len(all_files))))
    return all_files


# 2. Determine the maximum file width for display based on terminal width
def get_max_file_width_for_display():
    term_width = get_term_width()
    return term_width - 80 if term_width > 130 else term_width - 60


# 3. Process each file with progress indication
def process_files_with_progress(files, process_func, results, args, is_read_only):
    max_file_width = get_max_file_width_for_display()
    with Progress(console=get_console()) as progress:
        task = progress.add_task("", total=len(files))
        for i, file_path in enumerate(files):
            if not is_read_only:
                if not is_allowed_to_continue(file_path, args.allow_no_repo, args.allow_dirty, args.allow_not_tracked):
                    continue

            formatted_file = format_filename_for_display(file_path, max_file_width)
            progress_description = _tr("Processing file [green]#%03d[/] with name [green]%s[/]") % (i, formatted_file)
            progress.update(task, completed=i, description=progress_description)
            log.debug(_tr("Processing file [green]#%03d[/] with name [green]%s[/]") % (i, file_path))
            process_func(file_path, results, args)


def format_filename_for_display(file, max_file_width):
    if len(file) > max_file_width:
        return "..." + file[-(max_file_width - 5):]
    else:
        return file.ljust(max_file_width)


def map_alias_to_command(args, cmd_attr_name, aliases):
    for cmd in aliases:
        command = getattr(args, cmd_attr_name)
        if command in aliases[cmd]:
            setattr(args, cmd_attr_name,  cmd)

