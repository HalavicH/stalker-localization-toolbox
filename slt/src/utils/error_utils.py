from src.log_config_loader import log

failed_files = {}


def log_and_save_error(file: str, colored_message: str, level: str='error'):
    log.error(f"File: '{file}'")
    log.error("\t" + colored_message)

    # TODO: save and process level
    if failed_files.get(file) is None:
        failed_files[file] = [colored_message]
    else:
        failed_files[file].append(colored_message)


def clear_saved_errors():
    failed_files.clear()


def log_saved_errors():
    if len(failed_files) == 0:
        return

    log.error("#" * 80)
    log.error("\t\t\tFailed files errors:")
    log.error("#" * 80)
    for file in failed_files:
        log.error(f"File: '{file}'")
        for issue in failed_files[file]:
            log.error("\t" + issue)
