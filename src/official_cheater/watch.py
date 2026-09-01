import json
import subprocess
import sys

from . import debug


def launch_subprocesses(commands: list[dict]) -> None:
    """Launches subprocess based on list passed in.

    Args:
        commands: List of dictionaries that list the program arguements
        to spawn as separate tasks
    """

    try:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "official_cheater.watcher_process",
                r"C:\Users\daniel\Desktop\test_dir",
                commands[0]["command"],
                *commands[0]["arguments"],
            ],
            creationflags=(subprocess.CREATE_NEW_CONSOLE if debug.is_set() else 0),
        )

        print(f"Started watcher PID {process.pid} {commands[0]['arguments']}")

    except Exception as exc:
        print(f"Failed to start subprocess: {type(exc).__name__}: {exc}")


def run_watchers(args) -> None:
    """Spawns subprocess to watch and stamp directories as files are added to them

    Args:
        args: Command-line arguments. See __cli__.py for the current list
            of arguments and their types.
    """
    print(args) if args.debug else None

    if args.control == "stop":
        print("stop")

    elif args.control == "status":
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    "Get-CimInstance Win32_Process | "
                    "Where-Object {$_.CommandLine -like '*official_cheater.watch*'} | "
                    "Select-Object -ExpandProperty ProcessId"
                ),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        print(result.stdout)

    else:
        # open config file and spawn processess
        try:
            with args.control.open(encoding="utf-8") as f:
                config = json.load(f)

                launch_subprocesses(config["watches"])

        except OSError as exc:
            print(f"Unable to open {args.control}: {exc}")
