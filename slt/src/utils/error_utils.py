from src.log_config_loader import log

failed_files = {}


def log_and_save_error(file: str, colored_message: str):
    log.error(f"\nFile: '{file}'")
    for issue in failed_files[file]:
        log.error("\t" + issue)

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
    log.error("\t\t\tFailed files:")
    for file in failed_files:
        log.error(f"\nFile: '{file}'")
        for issue in failed_files[file]:
            log.error("\t" + issue)
