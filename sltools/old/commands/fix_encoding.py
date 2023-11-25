from sltools.old.config import PRIMARY_ENCODING
from sltools.old.commands.validate_encoding import validate_encoding
from sltools.log_config_loader import log
from sltools.utils.colorize import cf_yellow, cf_green, cf_red, cf_cyan
from sltools.utils.error_utils import log_and_save_error, display_encoding_error_details
from sltools.utils.file_utils import read_xml
from sltools.utils.git_utils import is_allowed_to_continue
from sltools.utils.lang_utils import trn  # Ensure this import is included for _tr function

def change_file_encoding(file_name, e_from, e_to):
    with open(file_name, 'r', encoding=e_from) as file:
        data = file.read()

    try:
        with open(file_name, 'w', encoding=e_to) as file:
            file.write(data)
    except UnicodeEncodeError as e:
        # Rollback
        log.warning(trn("Can't change encoding for %s. Rolling back...") % file_name)
        with open(file_name, 'w', encoding=e_from) as file:
            file.write(data)
        # Rethrow
        raise e

def fix_encoding(args, is_read_only):
    results = validate_encoding(args, is_read_only)

    log.always("")
    log.always(trn("All files analyzed! Fixing encodings..."))

    log.always(cf_yellow(trn("NOTE! Currently, reliable detection is only available for UTF-8 encoding.")))
    log.always(trn("For other suspicious files, manual review and encoding correction may be necessary."))

    results = list(filter(lambda t: t[1].lower() == 'utf-8', results))
    if len(results) == 0:
        log.always(trn("Nothing to fix"))
        return

    log.always(cf_green(trn("There is/are %d file(s) to fix") % len(results)))

    for file_name, encoding, comment in results:
        if encoding.lower() == "utf-8":
            if not is_read_only:
                if not is_allowed_to_continue(file_name, args.allow_no_repo, args.allow_dirty, args.allow_not_tracked):
                    continue
            windows_ = 'Windows-1251'
            log.always(trn("Try to change encoding from %s to %s for file %s") % (cf_red(encoding), cf_green(windows_), cf_cyan(file_name)))
            try:
                change_file_encoding(file_name, e_from=encoding, e_to=PRIMARY_ENCODING)
                log.always(cf_green(trn("Success!")))
            except (UnicodeEncodeError, UnicodeDecodeError) as e:
                log_and_save_error(file_name, trn("Can't encode from %s to %s") % (cf_yellow(encoding), cf_yellow(windows_)))
                display_encoding_error_details(read_xml(file_name, encoding), str(e))
        else:
            log.debug(trn("File %s possibly has %s encoding. But maybe no, so won't do anything") % (file_name, encoding))
