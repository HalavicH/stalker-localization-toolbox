from src.config import PRIMARY_ENCODING
from src.commands.validate_encoding import validate_encoding
from src.log_config_loader import log
from src.utils.colorize import cf_yellow, cf_green, cf_red, cf_cyan
from src.utils.error_utils import log_and_save_error, display_encoding_error_details
from src.utils.file_utils import read_xml
from src.utils.git_utils import is_allowed_to_continue


def change_file_encoding(file_name, e_from, e_to):
    with open(file_name, 'r', encoding=e_from) as file:
        data = file.read()

    try:
        with open(file_name, 'w', encoding=e_to) as file:
            file.write(data)
    except UnicodeEncodeError as e:
        # Rollback
        log.warning(f"Can't change encoding for {file_name}. Rolling back...")
        with open(file_name, 'w', encoding=e_from) as file:
            file.write(data)
        # Rethrow
        raise e


def fix_encoding(args, is_read_only):
    results = validate_encoding(args, is_read_only)

    log.always("")
    log.always("All files analyzed! Fixing encodings...")

    log.always(cf_yellow("NOTE! Currently, reliable detection is only available for UTF-8 encoding."))
    log.always("For other suspicious files, manual review and encoding correction may be necessary.")

    results = list(filter(lambda t: t[1].lower() == 'utf-8', results))
    if len(results) == 0:
        log.always("Nothing to fix")
        return

    log.always(cf_green(f"There is/are {len(results)} file(s) to fix"))

    for file_name, encoding, comment in results:
        if encoding.lower() == "utf-8":
            if not is_read_only:
                if not is_allowed_to_continue(file_name, args.allow_no_repo, args.allow_dirty, args.allow_not_tracked):
                    continue
            windows_ = 'Windows-1251'
            log.always(f"Try to change encoding from {cf_red(encoding)} to {cf_green(windows_)} for file {cf_cyan(file_name)}")
            try:
                change_file_encoding(file_name, e_from=encoding, e_to=PRIMARY_ENCODING)
                log.always(cf_green("Success!"))
            except (UnicodeEncodeError, UnicodeDecodeError) as e:
                log_and_save_error(file_name,
                                   f"Can't encode from {cf_yellow(encoding)} to {cf_yellow(windows_)}")
                display_encoding_error_details(read_xml(file_name, encoding), str(e))
        else:
            log.debug(f"File {file_name} possibly has {encoding} encoding. But maybe no, so won't do anything")
