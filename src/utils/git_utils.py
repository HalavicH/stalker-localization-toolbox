import os

try:
    import git
except ImportError as e:
    print("Can't import git module. In seems that git is not installed")

import subprocess

from rich import get_console

from src.log_config_loader import log
from src.utils.colorize import cf_cyan

skipped_files = []


def save_git_skipped_file(file: str, reason: str = ""):
    skipped_files.append((reason, file))


def clear_saved_errors():
    skipped_files.clear()


def log_skipped_files():
    if len(skipped_files) == 0:
        return

    log.warning("#" * 80)
    log.warning("\t\tSkipped files due to being dirty/not tracked by git:")
    log.warning("#" * 80)
    for reason, file in skipped_files:
        log.warning(f"\t{reason}: {file}")


def is_git_available():
    try:
        subprocess.run(['git', '--version'], check=True, text=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def is_file_unstaged(repo, relative_path):
    # status_output = repo.git.status('--porcelain', relative_path)
    unstaged_output = repo.git.diff(relative_path)
    return bool(unstaged_output)


def is_allowed_to_continue(path, allow_no_repo, allow_dirty, allow_not_tracked):
    console = get_console()

    if not allow_no_repo:
        if not is_git_available():
            console.print(
                "Git is not available on this system. It's vital to have files in a git repo to prevent potential file damage. Please install Git.")
            return False

    if not allow_no_repo:
        try:
            repo = git.Repo(path, search_parent_directories=True)
        except git.InvalidGitRepositoryError:
            log.warning(f"'It seems that there's no git repository here. Skipping the file processing. ")
            log_ignore_option("--allow-no-repo")
            save_git_skipped_file(path, "Not in repo")
            return False

        # Get the relative path of the file from the repository root
        relative_path = os.path.relpath(path, repo.working_tree_dir)

        if not allow_not_tracked:
            # Check if the file is tracked by git
            tracked_files_output = repo.git.ls_files(relative_path)
            if not tracked_files_output:
                log.warning(f"'File {path}' is not tracked by git. Skipping the file processing.")
                log_ignore_option("--allow-not-tracked")
                save_git_skipped_file(path, "Not tracked")
                return False

        if not allow_dirty:
            if is_file_unstaged(repo, relative_path):
                log.warning(
                    f"File '{path}' is dirty (modified but not staged/committed). Skipping the file processing.")
                log_ignore_option("--allow-dirty")
                save_git_skipped_file(path, "Dirty")
                return False

    return True  # It's safe to continue the script


def log_ignore_option(option):
    log.always(
        f"Note: If you sure you won't break anything, you can process this path anyway using {cf_cyan(option)}")
