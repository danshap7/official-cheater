"""Handles the 'watch' options for the official-cheater tools."""

import json
import subprocess
import sys

import psutil

from . import debug


def launch_subprocesses(watches: list[dict]) -> None:
    """Launches subprocess based on list passed in.

    Args:
        commands: List of dictionaries that list the program arguments
        to spawn as separate tasks
    """

    for watch in watches:
        try:
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "official_cheater.watcher_process",
                    watch["directory"],
                    watch["extension"],
                    watch["exclusion_text"],
                    watch["command"],
                    *watch["arguments"],
                ],
                creationflags=(
                    subprocess.CREATE_NEW_CONSOLE
                    if debug.is_set()
                    else subprocess.CREATE_NO_WINDOW
                ),
            )

            print(
                f"Started watcher PID {process.pid} on {watch['directory']} with {watch['command']} {watch['arguments']}"
            )

        except OSError as e:
            print(f"Failed to start subprocess: {type(e).__name__}: {e}")


def run_status() -> None:
    """runs the 'watch --status' commandline option
    Displays all running process of official_cheater.watcher_process
    """

    for process in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            # in the off chance that commadline is None
            cmdline = process.info["cmdline"] or []

            if "official_cheater.watcher_process" in cmdline:
                print(f"PID {process.info['pid']}: {' '.join(cmdline)}")

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # TODO needs better error handling
            # should other exceptions be handled?
            pass


def is_killed_pid(kill_list: list, current_pid) -> bool:
    """return true if list contains 'all' anywhere or the
    current_pid is in the list
    """

    return "all" in kill_list or current_pid in kill_list


def run_stop(stop: list) -> None:
    """runs the 'watch --stop' commandline option.  Kills watcher processes.

    Args:
        stop: A list containing 'all' or one or more PIDs to kill
    """

    for process in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            # in the off chance that commadline is None
            cmdline = process.info["cmdline"] or []

            if "official_cheater.watcher_process" in cmdline and is_killed_pid(
                stop, process.info["pid"]
            ):
                process.kill()
                process.wait(timeout=3)  # Wait for process to terminate

                print(f"Killed PID {process.info['pid']}: {' '.join(cmdline)}")

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # TODO needs better error handling
            # should other exceptions be handled?
            pass


def run_watchers(args) -> None:
    """Spawns subprocess to watch and stamp directories as files are added to them

    Args:
        args: Command-line arguments. See __cli__.py for the current list
            of arguments and their types.
    """

    print(args) if args.debug else None

    if args.stop:
        run_stop(args.stop)

    elif args.status:
        run_status()

    else:
        # open config file and spawn processess
        try:
            with args.start.open(encoding="utf-8") as f:
                config = json.load(f)

                launch_subprocesses(config["watches"])

        except OSError as exc:
            print(f"Unable to open {args.control}: {exc}")

        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
