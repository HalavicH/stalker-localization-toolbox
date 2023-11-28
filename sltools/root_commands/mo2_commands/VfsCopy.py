import os
import shutil

from sltools.baseline.command_baseline import AbstractCommand
from sltools.log_config_loader import log
from sltools.utils.lang_utils import trn


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
            log.warning(trn("Source file not found: %s") % source)
            return False
        shutil.copy2(source, destination)
        return True
    except Exception as e:
        log.error(trn("Error copying file from %s to %s: %s") % (source, destination, str(e)))
        return False


class VfsCopy(AbstractCommand):
    # Metadata
    ##########
    def get_name(self) -> str:
        return "vfs-copy"

    def get_aliases(self) -> list:
        return ['vc']

    def _get_help(self) -> str:
        return trn('Create a physical copy of the MO2 VFS using a list of real file paths')

    def _setup_parser_args(self, parser):
        parser.add_argument('--real-paths-file', required=True, dest="real_paths_file",
                            help=trn('Path to the file containing real paths of the VFS (output from vfs-map command)'))
        parser.add_argument('--mo2-base-dir', required=True, dest="mo2_base_dir",
                            help=trn('Path to the base directory of Mod Organizer 2'))
        parser.add_argument('--output-dir', required=True, dest="output_dir",
                            help=trn('Directory where the physical copy of the VFS will be created'))

        # Create a mutually exclusive group for the mode of operation
        mode_group = parser.add_mutually_exclusive_group(required=True)
        mode_group.add_argument('--merge', action='store_true',
                                help=trn('Merge all files into a single directory, replicating the unified VFS view'))
        mode_group.add_argument('--keep-structure', action='store_true',
                                help=trn('Retain the original mod directory structure in the output, useful for identifying file sources'))

    # Execution
    ###########
    def _process_file(self, file_path, results: dict, args):
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

    def execute(self, args) -> dict:
        with open(args.real_paths_file, 'r', encoding='utf-8') as file:
            file_paths = file.readlines()

        if os.path.exists(args.output_dir) and os.listdir(args.output_dir):
            user_response = input(trn("Output directory '%s' already exists. Do you want to override it? [y/N]: ") % args.output_dir)
            if user_response.lower() != 'y':
                log.always(trn("Operation cancelled by user."))
                return {}

        results = {'copied_files': 0, 'skipped_files': 0}
        # is_read_only == True because command doesn't modify existing repo.
        self.process_files_with_progressbar(args, file_paths, results, True)

        log.always(trn("Processed file tree from '%s' to '%s'.\nTotal files copied: %d\nTotal files skipped: %d") %
                   (args.real_paths_file, args.output_dir, results['copied_files'], results['skipped_files']))

        return {}

    # Displaying
    ############
    def display_result(self, result: dict):
        pass
