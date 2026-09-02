import subprocess
import sys
import time
from pathlib import Path


def wait_for_file(file: Path, stable_time: float = 2.0) -> bool:
    """Wait until a file has stopped changing.  Some of our longer PDFs can
    still be in the middle of initial writing while we're trying to open them"""
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

        time.sleep(0.5)


def watch_directory(
    directory: str, ext: str, exclude: str, command: str, arguments: list[str]
) -> None:
    """call passed command with arguments when 'directory' is written to"""

    watch_path: Path = Path(directory)
    existing_files = set(watch_path.iterdir())

    print(f"Watcher starting: {directory}")
    print(f"Path exists: {watch_path.exists()}")
    print(f"Arguments: {arguments}")

    while True:
        current_files = set(watch_path.iterdir())
        added_files = current_files - existing_files

        for file in added_files:
            # only trigger on PDFs that have stopped updating
            # and do not contain '_stamped' in the filename
            # i.e. not files we stamped
            if (
                file.is_file()
                and file.suffix.casefold() == ext
                and exclude not in file.name.casefold()
                and wait_for_file(file)
            ):
                proc_cmd = [
                    command,
                    arguments[0],
                    str(file),
                ] + arguments[1:]

                print(f"NEW: {file} CMD: {command} {', '.join(arguments)}")

                try:
                    subprocess.run(
                        proc_cmd,
                        check=True,
                    )
                except OSError as e:
                    print(f"Failed to start subprocess: {type(e).__name__}: {e}")

        existing_files = current_files
        time.sleep(2)


if __name__ == "__main__":
    for i in range(len(sys.argv)):
        print(sys.argv[i])

    watch_directory(
        directory=sys.argv[1],
        ext=sys.argv[2],
        exclude=sys.argv[3],
        command=sys.argv[4],
        arguments=sys.argv[5:],
    )
