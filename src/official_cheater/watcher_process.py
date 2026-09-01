import sys
import subprocess
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


def watch_directory(directory: str) -> None:
    path = Path(directory)
    existing = set(path.iterdir())

    print(f"Watcher starting: {directory}", flush=True)
    print(f"Path exists: {path.exists()}", flush=True)

    while True:
        current = set(path.iterdir())
        added = current - existing

        for file in added:

            # only trigger on PDFs that have stopped updating
            # and do not contain '_stamped' in the filename
            # i.e. not files we stamped
            if (
                file.is_file()
                and file.suffix.casefold() == ".pdf"
                and "_stamped" not in file.name.casefold()
                and wait_for_file(file)
            ):
                print("new")

                command = [ "official-cheater",
                            "stamp",
                            str(file),
                            "-a",
                            r".\pdf\upper_right__order_of_finish.pdf",
                            "-e",
                            r".\pdf\lower_right__closeout.pdf",
                        ]

                try:
                    subprocess.run(
                        command,
                        check=True,
                    )    
                except Exception as exc:
                    print(f"Failed to start subprocess: {type(exc).__name__}: {exc}")

        existing = current
        time.sleep(2)


if __name__ == "__main__":
    for i in range(len(sys.argv)):
        print(sys.argv[i])

    watch_directory(sys.argv[1])
