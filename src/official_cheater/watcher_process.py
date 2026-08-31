import sys
import time
from pathlib import Path


def watch_directory(directory: str) -> None:
    path = Path(directory)
    existing = set(path.iterdir())

    print(f"Watcher starting: {directory}", flush=True)
    print(f"Path exists: {path.exists()}", flush=True)

    while True:
        current = set(path.iterdir())
        added = current - existing

        for file in added:
            if file.is_file():
                print("new")
                with open(file, "w") as f:
                    f.write("this is new")

        existing = current
        time.sleep(10)


if __name__ == "__main__":
    for i in range(len(sys.argv)):
        print(sys.argv[i])

    watch_directory(sys.argv[1])
