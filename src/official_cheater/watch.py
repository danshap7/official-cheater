import argparse
import json
import subprocess
import sys
from pathlib import Path

from . import debug


def load_watcher_config(filename: Path) -> list[dict]:
    with filename.open(encoding="utf-8") as f:
        config = json.load(f)

    return config["watches"]


def launch_subprocesses(commands: list[dict]) -> None:

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "official_cheater.watcher_process",
            r"C:\Users\Daniel\Desktop",
            commands[0]["command"],
            *commands[0]["arguments"],
        ],
        creationflags=(subprocess.CREATE_NEW_CONSOLE if debug.is_set() else 0),
    )

    print(f"Started watcher PID {process.pid} {commands[0]['arguments']}")


def run_watchers(args: argparse.Namespace) -> None:
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
        )

        print(result.stdout)

    else:
        out: list[dict] = load_watcher_config(args.control)

        launch_subprocesses(out)
