import os

from sltools.utils.lang_utils import trn

try:
    import git
except ImportError as e:
    print(trn("Can't import git module. In seems that git is not installed"))

import subprocess
from rich import get_console
from sltools.log_config_loader import log
from sltools.utils.colorize import cf_cyan
from sltools.utils.lang_utils import trn

skipped_files = []


def save_git_skipped_file(file: str, reason: str = ""):
    skipped_files.append((reason, file))


def clear_saved_errors():
    skipped_files.clear()


def log_skipped_files():
    if len(skipped_files) == 0:
        return

    log.warning("#" * 80)
    log.warning(trn("\tSkipped files due to being dirty/not tracked by git:"))
    log.warning("#" * 80)
    for reason, file in skipped_files:
        log.warning(trn("\t%s: %s") % (reason, file))


def is_git_available():
    try:
        subprocess.run(['git', '--version'], check=True, text=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def is_file_unstaged(repo, relative_path):
    unstaged_output = repo.git.diff(relative_path)
    return bool(unstaged_output)


def is_allowed_to_continue(path, allow_no_repo, allow_dirty, allow_not_tracked):
    console = get_console()

    if not allow_no_repo:
        if not is_git_available():
            console.print(
                trn("Git is not available on this system. It's vital to have files in a git repo to prevent potential file damage. Please install Git."))
            return False

    if not allow_no_repo:
        try:
            repo = git.Repo(path, search_parent_directories=True)
        except git.InvalidGitRepositoryError:
            log.warning(trn("'It seems that there's no git repository here. Skipping the file processing. "))
            log_ignore_option("--allow-no-repo")
            save_git_skipped_file(path, "Not in repo")
            return False

        relative_path = os.path.relpath(path, repo.working_tree_dir)

        if not allow_not_tracked:
            tracked_files_output = repo.git.ls_files(relative_path)
            if not tracked_files_output:
                log.warning(trn("'File %s' is not tracked by git. Skipping the file processing.") % path)
                log_ignore_option("--allow-not-tracked")
                save_git_skipped_file(path, "Not tracked")
                return False

        if not allow_dirty:
            if is_file_unstaged(repo, relative_path):
                log.warning(trn("File '%s' is dirty (modified but not staged/committed). Skipping the file processing.") % path)
                log_ignore_option("--allow-dirty")
                save_git_skipped_file(path, trn("Dirty"))
                return False

    return True


def log_ignore_option(option):
    log.always(trn("Note: If you sure you won't break anything, you can process this path anyway using %s") % cf_cyan(option))
