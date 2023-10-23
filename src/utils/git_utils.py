import os

import git
import subprocess

from rich import get_console

from src.log_config_loader import log


def is_git_available():
    try:
        subprocess.run(['git', '--version'], check=True, text=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def is_file_dirty(repo, relative_path):
    status_output = repo.git.status('--porcelain', relative_path)
    return bool(status_output)  # If status_output is non-empty, the file is dirty


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
            console.print(f"'{path}' is not within a git repository")
            return False

        # Get the relative path of the file from the repository root
        relative_path = os.path.relpath(path, repo.working_tree_dir)

        if not allow_not_tracked:
            # Check if the file is tracked by git
            tracked_files_output = repo.git.ls_files(relative_path)
            if not tracked_files_output:
                console.print(f"'{path}' is not tracked by git")
                return False

        if not allow_dirty:
            if is_file_dirty(repo, relative_path):
                console.print(f"'{path}' is dirty (modified but not staged/committed)")
                return False

    return True  # It's safe to continue the script
