from log_config_loader import get_main_logger

log = get_main_logger()

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
    print()
    print("#" * 80)
    print("\t\t\tFailed files:")
    for file in failed_files:
        print(f"\nFile: '{file}'")
        for issue in failed_files[file]:
            print("\t" + issue)
