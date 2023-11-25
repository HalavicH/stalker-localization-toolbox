import sys

from sltools.log_config_loader import log
from sltools.utils.error_utils import log_saved_errors
from sltools.utils.git_utils import is_git_available, log_ignore_option, log_skipped_files
from sltools.utils.lang_utils import trn


def process_generic_cmd(args, command_name, registry):
    callback_data = registry.get(command_name)
    log.info(trn("Processing command: %s") % command_name)
    if callback_data is None:
        log.error(trn("Command '%s' is not implemented") % command_name)
        sys.exit(1)
    callback = callback_data["callback"]
    read_only = callback_data["read_only"]
    if not read_only and not args.allow_no_repo and not is_git_available():
        err = trn("Git is not available on this system. It's vital to have files in a git repo to prevent potential file damage. Please install Git.")
        log.error(err)
        log_ignore_option("--allow-no-repo")
        return False

        # Do actual work
    log.always(trn("Running command '%s'") % command_name)
    callback(args, read_only)

    log_skipped_files()
    log_saved_errors()

