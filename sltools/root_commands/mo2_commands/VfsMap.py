import os

from sltools.baseline.command_baseline import AbstractCommand
from sltools.log_config_loader import log
from sltools.utils.lang_utils import trn

STATS = {
    'total': 0,
    'included': 0,
    'excluded': 0,
}


class VfsMap(AbstractCommand):
    # Metadata
    ##########
    def get_name(self) -> str:
        return "vfs-map"

    def get_aliases(self) -> list:
        return ['vm']

    def _get_help(self) -> str:
        return trn('Map VFS file tree to physical file paths for MO2 mods')

    def _setup_parser_args(self, parser):
        parser.add_argument('--vfs-file', required=True, dest="vfs_file",
                            help=trn('Path to the VFS file tree report from MO2'))
        parser.add_argument('--output-file', required=True, dest="output_file",
                            help=trn('File to output the mapped physical file paths to'))
        # parser.add_argument('--merge', action='store_true',
        #                     help=trn('Combine all mod files into a single directory, mimicking the VFS structure.'))
        parser.add_argument('--exclude-patterns', dest='exclude_patterns',
                            help=trn('Exclude files or mods matching these patterns (separate multiple patterns with "|")'))
        parser.add_argument('--include-patterns', dest='include_patterns',
                            help=trn('Include only files or mods matching these patterns (separate multiple patterns with "|")'))

    # Execution
    ###########
    def _process_file(self, file_path, results: dict, args):
        pass


    @staticmethod
    def filter_lines(path, include_patterns, exclude_patterns):
        match = True if len(include_patterns) == 0 and len(exclude_patterns) == 0 else False

        # Include where filter matches
        for filter_str in include_patterns:
            if filter_str in path:
                match = True
                break

        # Exclude where match
        for filter_str in exclude_patterns:
            if filter_str[1:] not in path:
                continue
            else:
                match = False

        if not match:
            log.debug("Skipping: " + path.strip())
            STATS['excluded'] += 1
        else:
            log.debug("Including: " + path.strip())
            STATS['included'] += 1

        STATS['total'] += 1
        return match

    @staticmethod
    def process_file_tree(input_file_path, output_file_path, include_patterns, exclude_patterns):
        # Output file will be in the same directory as the input file
        output_file_path = os.path.join(os.path.dirname(input_file_path), output_file_path)

        with open(input_file_path, 'r', encoding='utf-8') as input_file, \
                open(output_file_path, 'w', encoding='utf-8') as output_file:

            filtered_lines = filter(lambda path: VfsMap.filter_lines(path, include_patterns, exclude_patterns), input_file)

            for line in filtered_lines:
                # Splitting the line to separate the file path and the mod info
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    file_path, mod_info = parts
                    mod_name = mod_info.strip().strip('()')
                    # Remove the 'Data' folder and construct the real file path
                    file_path = file_path.replace('Data\\', '')
                    real_path = f".\\mods\\{mod_name}\\{file_path}"

                    output_file.write(real_path + '\n')

        return output_file_path

    def execute(self, args) -> dict:
        include_patterns = args.include_patterns.split("|") if args.include_patterns else []
        exclude_patterns = args.exclude_patterns.split("|") if args.exclude_patterns else []

        input_file = args.vfs_file
        output_path = args.output_file

        log.always(trn("Mapping MO2 VFS paths to real"))
        log.always(trn("\tFile with mappings: %s") % input_file)
        log.always(trn("\tResulting file: %s") % output_path)
        log.always(trn("\tInclude: %s") % include_patterns)
        log.always(trn("\tExclude: %s") % exclude_patterns)

        VfsMap.process_file_tree(input_file, output_path, include_patterns, exclude_patterns)

        log.always(trn("Converted file paths saved to: %s") % output_path)
        log.always(trn("Processed: %d file entries. Included: %d, excluded: %d") % (STATS['excluded'], STATS['included'], STATS['total']))

        return {}

    # Displaying
    ############
    def display_result(self, result: dict):
        pass
