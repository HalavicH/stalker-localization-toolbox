import os
import shutil

from rich import get_console

from sltools.commands.utils.common import process_files_with_progress
from sltools.log_config_loader import log
from sltools.utils.lang_utils import _tr  # Ensure this import is included for _tr function


def copy_file(source, destination):
    """Copy a file from source to destination.

    Args:
        source (str): Path to the source file.
        destination (str): Path to the destination.

    Returns:
        bool: True if file was successfully copied, False otherwise.
    """
    try:
        if not os.path.exists(source):
            log.warning(_tr("Source file not found: %s") % source)
            return False
        shutil.copy2(source, destination)
        return True
    except Exception as e:
        log.error(_tr("Error copying file from %s to %s: %s") % (source, destination, str(e)))
        return False


def process_file(file_path, results, args):
    relative_path = file_path.strip()[2:]  # Remove '.\' at the beginning
    source_path = os.path.join(args.mo2_base_dir, relative_path)

    if args.merge:
        # Skip the mod's name (first folder) in the path
        path_parts = relative_path.split(os.sep)[1:]  # Split and remove the first part
        merged_relative_path = os.path.join(*path_parts)  # Rejoin the remaining parts
        dest_path = os.path.join(args.output_dir, 'Data', merged_relative_path)
    else:
        dest_path = os.path.join(args.output_dir, relative_path)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    copy_success = copy_file(source_path, dest_path)
    if copy_success:
        results['copied_files'] += 1
    else:
        results['skipped_files'] += 1


def vfs_copy(args, is_read_only):
    with open(args.real_paths_file, 'r', encoding='utf-8') as file:
        file_paths = file.readlines()

    if os.path.exists(args.output_dir) and os.listdir(args.output_dir) and not is_read_only:
        user_response = input(_tr("Output directory '%s' already exists. Do you want to override it? [y/N]: ") % args.output_dir)
        if user_response.lower() != 'y':
            log.always(_tr("Operation cancelled by user."))
            return

    results = {'copied_files': 0, 'skipped_files': 0}
    process_files_with_progress(file_paths, process_file, results, args, is_read_only)

    log.always(_tr("Processed file tree from '%s' to '%s'.\nTotal files copied: %d\nTotal files skipped: %d") %
               (args.real_paths_file, args.output_dir, results['copied_files'], results['skipped_files']))

    # Log results
    log.always(_tr("Processed file tree from '%s' to '%s'.\nTotal files copied: %d\nTotal files skipped: %d") %
               (args.real_paths_file, args.output_dir, results['copied_files'], results['skipped_files']))

# Example usage
# args = ...  # Args should be an object with the necessary attributes
# is_read_only = False  # Set to True to prevent actual file copying (for dry run)
# vfs_copy(args, is_read_only)
