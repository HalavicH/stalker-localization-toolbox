import os

from sltools.log_config_loader import log
from sltools.utils.lang_utils import _tr

STATS = {
    'total': 0,
    'included': 0,
    'excluded': 0,
}


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


def process_file_tree(input_file_path, output_file_path, include_patterns, exclude_patterns):
    # Output file will be in the same directory as the input file
    filename = os.path.basename(input_file_path)
    output_file_path = os.path.join(os.path.dirname(input_file_path), output_file_path)

    with open(input_file_path, 'r', encoding='utf-8') as input_file, \
            open(output_file_path, 'w', encoding='utf-8') as output_file:

        filtered_lines = filter(lambda path: filter_lines(path, include_patterns, exclude_patterns), input_file)

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


def vfs_map(args, is_read_only):
    include_patterns = args.include_patterns.split("|") if args.include_patterns else []
    exclude_patterns = args.exclude_patterns.split("|") if args.exclude_patterns else []

    input_file = args.vfs_file
    output_path = args.output_file

    log.always(_tr("Mapping MO2 VFS paths to real"))
    log.always(_tr("\tFile with mappings: %s") % input_file)
    log.always(_tr("\tResulting file: %s") % output_path)
    log.always(_tr("\tInclude: %s") % include_patterns)
    log.always(_tr("\tExclude: %s") % exclude_patterns)

    process_file_tree(input_file, output_path, include_patterns, exclude_patterns)

    log.always(_tr("Converted file paths saved to: %s") % output_path)
    log.always(_tr("Processed: %d file entries. Included: %d, excluded: %d") % (STATS['excluded'], STATS['included'], STATS['total']))
