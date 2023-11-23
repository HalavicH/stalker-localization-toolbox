# Command Registry
from sltools.commands.mo2.vfs_copy import vfs_copy
from sltools.commands.mo2.vfs_map import vfs_map
from sltools.commands.utils.common import map_alias_to_command
from sltools.commands.utils.process_generic_cmd import process_generic_cmd
from sltools.config import VFS_MAP, VFS_COPY, MO2_CMD_TO_ALIASES

MO2_CMD_REGISTRY = {
    VFS_MAP: {"callback": vfs_map, "read_only": True},
    VFS_COPY: {"callback": vfs_copy, "read_only": True},
}


def process_mo2(args, read_only):
    map_alias_to_command(args, "subcommand", MO2_CMD_TO_ALIASES)
    process_generic_cmd(args, args.subcommand, MO2_CMD_REGISTRY)
