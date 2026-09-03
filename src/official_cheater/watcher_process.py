"""Separate task to be spawned for watching for added files to a directory"""

import subprocess
import sys
import time
from pathlib import Path


def wait_for_file(
    file: Path, stable_time: float = 2.0, sleep_time: float = 0.5
) -> bool:
    """Wait until a file has stopped changing.  Some of our longer PDFs can
    still be in the middle of initial writing while we're trying to open them

    Args:
        file: File we're testing for done.
        stable_time: How long 'file' has not changed in size.  Default is 2-sec.
        sleep_time: How long to wait between file size changes.  Default is 0.5-sec.
    """

    last_size: int = -1
    stable_since: float = time.monotonic()

    while True:
        try:
            current_size: int = file.stat().st_size
        except FileNotFoundError:
            return False

        if current_size != last_size:
            last_size = current_size
            stable_since = time.monotonic()
        elif time.monotonic() - stable_since >= stable_time:
            return True

        time.sleep(sleep_time)


def watch_directory(
    directory: str,
    ext: str,
    exclude: str,
    command: str,
    arguments: list[str],
    watch_delay: float = 2.0,
) -> None:
    """call passed command with arguments when 'directory' is written to

    Args:
       directory: Directory we're monitoring.
       ext: Extension we'll trigger on.
       exclude: Ignore files with this string in it.
       command: Command to execute on valid files.
       arguments: Arguments passed to 'command'.
       watch_delay: How long to wait between file checks.  Default is 2-sec.
    """

    watch_path: Path = Path(directory)

    if not watch_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {watch_path}")

    if not watch_path.exists():
        raise FileNotFoundError(f"Directory does not exist: {watch_path}")

    existing_files = set(watch_path.iterdir())

    print(f"Watcher started on: {directory}")
    print(f"Command: {command}")
    print(f"Arguments: {arguments}")

    # fold everything to lower case
    ext = ext.casefold()
    exclude = exclude.casefold()

    while True:
        current_files = set(watch_path.iterdir())
        added_files = current_files - existing_files

        for file in added_files:
            # only trigger on PDFs that have stopped updating
            # and do not contain '_stamped' in the filename
            # i.e. not files we stamped

            if (
                file.is_file()
                and ext == file.suffix.casefold()
                and exclude not in file.name.casefold()
                and wait_for_file(file)
            ):
                proc_cmd = [
                    command,
                    arguments[0],
                    str(file),
                ] + arguments[1:]

                print(f"\nNEW: {file} CMD: {command} {', '.join(arguments)}")

                try:
                    subprocess.run(
                        proc_cmd,
                        check=True,
                    )
                except OSError as e:
                    print(f"Failed to start subprocess: {type(e).__name__}: {e}")

        existing_files = current_files
        time.sleep(watch_delay)


if __name__ == "__main__":
    """ This is the entry point from launch_subprocesses() in watch.py"""
    watch_directory(
        directory=sys.argv[1],
        ext=sys.argv[2],
        exclude=sys.argv[3],
        command=sys.argv[4],
        arguments=sys.argv[5:],
    )
